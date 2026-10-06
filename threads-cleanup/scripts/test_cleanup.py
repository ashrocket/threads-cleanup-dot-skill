"""Browser fixture tests: no connection to real Threads or TypeSafe."""
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from playwright.sync_api import sync_playwright
from threads_cleanup import BASE, Cleanup, own_post, post_path


class FakeJev:
    def choose(self, operation, labels):
        if operation == "delete" and "Delete" in labels:
            return "delete"
        if operation == "unsave" and "Unsave" in labels:
            return "unsave"
        if operation == "unsave" and "Save" in labels:
            return "already_unsaved"
        raise RuntimeError("Missing authorized control")


class CleanupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pw = sync_playwright().start()
        cls.browser = cls.pw.chromium.launch(channel="chrome", headless=True)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.pw.stop()

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.context = self.browser.new_context()
        self.page = self.context.new_page()
        self.deleted = set()
        self.saved = True
        self.account = "demo_user"
        self.delete_clicks = 0
        self.context.route("https://www.threads.com/**", self.route)
        self.args = SimpleNamespace(account="demo_user", state=Path(self.tmp.name), execute=True, phases="posts,replies,saved", delay=1, limit=0)
        self.runner = Cleanup(self.page, self.args, FakeJev())

    def tearDown(self):
        self.context.close()
        self.tmp.cleanup()

    def route(self, route):
        from urllib.parse import urlsplit, parse_qs
        u = urlsplit(route.request.url)
        if u.path == "/mutate":
            q = parse_qs(u.query)
            if q["op"][0] == "delete":
                self.deleted.add(q["target"][0])
                self.delete_clicks += 1
            else:
                self.saved = False
            route.fulfill(body="ok")
            return
        target = "/@demo_user/post/P1"
        if u.path.startswith("/@other") or u.path.startswith("/saved"):
            target = "/@other/post/S1"
        elif u.path.endswith("replies") or u.path.endswith("R1"):
            target = "/@demo_user/post/R1"
            if u.path.endswith("replies") and target in self.deleted:
                target = "/@demo_user/post/R2"
        elif u.path == "/@demo_user" and target in self.deleted:
            target = "/@demo_user/post/P2"
        detail = "/post/" in u.path
        exists = target not in self.deleted and (not u.path.startswith("/saved") or self.saved)
        content = "<p>Sorry, this page isn't available.</p>" if detail else "<p>You haven't posted any threads yet</p>"
        if exists:
            labels = ["Copy link", "Unsave" if self.saved else "Save", "Report"] if "other" in target else ["Save", "Archive", "Delete"]
            content = f'''<article><a href="{target}"><time>Today</time></a><button aria-label="More" onclick="document.querySelector('#menu').hidden=false">•••</button><p>Example post</p></article>
            <div id="menu" role="menu" hidden>{''.join(f'<button role="menuitem" onclick="selectControl({json.dumps(label).replace(chr(34), chr(39))})">{label}</button>' for label in labels)}</div>
            <div id="confirm" hidden><h2>Delete post?</h2><button onclick="mutate('delete')">Delete</button><button>Cancel</button></div>
            <script>
            function selectControl(label){{if(label==='Delete'){{document.querySelector('#menu').hidden=true;document.querySelector('#confirm').hidden=false}} else if(label==='Unsave'){{mutate('unsave')}}}}
            async function mutate(op){{await fetch('/mutate?op='+op+'&target='+encodeURIComponent('{target}'));document.querySelector('article').remove();document.querySelector('#menu').hidden=true;document.querySelector('#confirm').hidden=true}}
            </script>'''
        html = f'<html><body><a href="/@{self.account}" aria-label="Profile">Profile</a><button>Edit profile</button><section role="region" aria-label="Column body">{content}</section></body></html>'
        route.fulfill(content_type="text/html", body=html)

    def test_delete_verify_and_resume(self):
        self.runner.apply("/@demo_user/post/P1", "delete")
        self.assertIn("/@demo_user/post/P1", self.deleted)
        self.assertEqual(self.delete_clicks, 1)
        # Simulates a crash after the website succeeded but before checkpoint commit.
        resumed = Cleanup(self.page, self.args, FakeJev())
        resumed.finish_pending()
        self.assertEqual(self.delete_clicks, 1)
        self.assertIsNone(resumed.state["pending"])
        self.assertIn("delete:/@demo_user/post/P1", resumed.state["done"])

    def test_unsave_only(self):
        self.runner.apply("/@other/post/S1", "unsave")
        self.assertFalse(self.saved)
        self.assertEqual(self.delete_clicks, 0)

    def test_pending_reply_verified_from_loaded_feed(self):
        self.deleted.add("/@demo_user/post/R1")
        self.runner.state["pending"] = {"target": "/@demo_user/post/R1", "operation": "delete", "phase": "replies"}
        self.runner.save()
        self.assertTrue(self.runner.finish_pending())
        self.assertEqual(self.delete_clicks, 0)
        self.assertIn("delete:/@demo_user/post/R1", self.runner.state["done"])

    def test_pending_post_verified_from_loaded_feed(self):
        self.deleted.add("/@demo_user/post/P1")
        self.runner.state["pending"] = {"target": "/@demo_user/post/P1", "operation": "delete", "phase": "posts"}
        self.runner.save()
        self.assertTrue(self.runner.finish_pending())
        self.assertEqual(self.delete_clicks, 0)
        self.assertIn("delete:/@demo_user/post/P1", self.runner.state["done"])

    def test_dry_run_does_not_mutate(self):
        self.args.execute = False
        self.runner.apply("/@demo_user/post/P1", "delete")
        self.assertEqual(self.deleted, set())
        self.assertIsNone(self.runner.state["pending"])

    def test_wrong_owner_rejected(self):
        with self.assertRaisesRegex(RuntimeError, "another account"):
            self.runner.apply("/@other/post/S1", "delete")
        self.assertEqual(self.delete_clicks, 0)

    def test_wrong_login_rejected(self):
        self.account = "someone_else"
        with self.assertRaisesRegex(RuntimeError, "Signed-in account"):
            self.runner.navigate("/@demo_user")

    def test_candidate_filter(self):
        self.page.set_content('<section role="region" aria-label="Column body"><a href="/@other/post/P0"><time>Now</time></a><a href="/@demo_user/post/R1"><time>Now</time></a><a href="/@other/post/Q1">Quoted post</a></section>')
        self.assertEqual(self.runner.candidates("replies"), ["/@demo_user/post/R1"])

    def test_last_post_empty_profile(self):
        self.page.goto(BASE + "/@demo_user")
        self.page.set_content('<button>Edit profile</button><section role="region" aria-label="Column body"><p>Finish your profile</p><button>Post</button></section>')
        self.assertTrue(self.runner.confirmed_empty_feed("posts"))
        self.assertFalse(self.runner.confirmed_empty_feed("replies"))

    def test_url_scope(self):
        self.assertFalse(own_post("/@demo_user_other/post/X", "demo_user"))
        self.assertIsNone(post_path("https://evil.example/@demo_user/post/X"))
        self.assertIsNone(post_path("/@demo_user/post/X/media"))


if __name__ == "__main__":
    unittest.main()
