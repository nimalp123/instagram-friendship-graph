import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from friendship_graph.cli import InputError, build, load_export, load_observations, prepare_second_degree, prepare_third_degree


def meta_rows(*names):
    return [{"string_list_data": [{"value": name, "href": f"https://instagram.com/{name}"}]} for name in names]


def meta_following_rows(*names):
    return [{"title": name, "string_list_data": [{"href": f"https://instagram.com/{name}"}]} for name in names]


class GraphTests(unittest.TestCase):
    def test_export_zip_and_three_hops(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            archive = base / "export.zip"
            with zipfile.ZipFile(archive, "w") as output:
                output.writestr("instagram/relationships/followers_and_following/followers_1.json", json.dumps(meta_rows("Alex", "bea", "only_follows_me")))
                output.writestr("instagram/relationships/followers_and_following/following.json", json.dumps({"relationships_following": meta_following_rows("alex", "bea", "only_i_follow")}))
            followers, following = load_export(archive)
            observations_file = base / "observations.json"
            observations_file.write_text(json.dumps([
                {"account": "alex", "followers": ["me", "casey"], "following": ["me", "casey"]},
                {"account": "casey", "followers": ["alex", "drew"], "following": ["alex", "drew"]},
                {"account": "drew", "followers": ["casey"], "following": ["casey"]},
            ]))
            observations = load_observations(observations_file, "me")
            vault = base / "vault"
            self.assertEqual(build("me", followers, following, observations, vault), {0: 1, 1: 2, 2: 1, 3: 1})
            self.assertFalse((vault / "People/only_follows_me.md").exists())
            self.assertFalse((vault / "People/only_i_follow.md").exists())
            self.assertIn("degree: 3", (vault / "People/drew.md").read_text())
            canvas = json.loads((vault / "Friendship Rings.canvas").read_text())
            self.assertEqual(len(canvas["nodes"]), 5)
            self.assertTrue(all(edge["toEnd"] == "none" for edge in canvas["edges"]))

    def test_incomplete_export_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary) / "followers_and_following"
            folder.mkdir()
            (folder / "followers_1.json").write_text(json.dumps(meta_rows("alex")))
            with self.assertRaises(InputError):
                load_export(folder)

    def test_observations_require_both_lists(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "observations.json"
            path.write_text(json.dumps([{"account": "alex", "followers": ["me"]}]))
            with self.assertRaises(InputError):
                load_observations(path, "me")

    def test_root_observation_can_be_loaded_for_export_comparison(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "observations.json"
            path.write_text(json.dumps([{"account": "me", "followers": ["alex"], "following": ["alex"]}]))
            self.assertEqual(len(load_observations(path, "me")), 1)

    def test_rebuild_removes_stale_generated_notes_and_protects_personal_notes(self):
        with tempfile.TemporaryDirectory() as temporary:
            vault = Path(temporary) / "vault"
            build("me", {"alex"}, {"alex"}, [], vault)
            (vault / "People" / "personal.md").write_text("My own note")
            build("me", set(), set(), [], vault)
            self.assertFalse((vault / "People/alex.md").exists())
            self.assertTrue((vault / "People/personal.md").exists())

    def test_second_degree_batch_excludes_observed_and_uses_recent_follow_order(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            archive = base / "export.zip"
            following = meta_following_rows("alex", "bea", "casey")
            for row, stamp in zip(following, [10, 30, 20]):
                row["string_list_data"][0]["timestamp"] = stamp
            with zipfile.ZipFile(archive, "w") as output:
                output.writestr("connections/followers_and_following/followers_1.json", json.dumps(meta_rows("alex", "bea", "casey")))
                output.writestr("connections/followers_and_following/following.json", json.dumps({"relationships_following": following}))
            observed = base / "observations.json"
            observed.write_text(json.dumps([{"account": "bea", "followers": [], "following": []}]))
            task = base / "local-data" / "second-degree-task.md"
            self.assertEqual(prepare_second_degree("me", archive, [observed], None, 2, task), ["casey", "alex"])
            self.assertIn("@casey", task.read_text())
            self.assertNotIn("@bea", task.read_text())
            targets = base / "targets.txt"
            targets.write_text("@alex\n")
            self.assertEqual(prepare_second_degree("me", archive, [observed], targets, 2, task), ["alex"])

    def test_third_degree_batch_uses_observed_paths_and_skips_inaccessible(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            archive = base / "export.zip"
            with zipfile.ZipFile(archive, "w") as output:
                output.writestr("connections/followers_and_following/followers_1.json", json.dumps(meta_rows("alex", "bea")))
                output.writestr("connections/followers_and_following/following.json", json.dumps({"relationships_following": meta_following_rows("alex", "bea")}))
            observed = base / "observations.json"
            observed.write_text(json.dumps([
                {"account": "alex", "followers": ["me", "casey", "drew"], "following": ["me", "casey", "drew"]},
                {"account": "bea", "followers": ["me", "drew"], "following": ["me", "drew"]},
            ]))
            task = base / "local-data" / "third-degree-batch-2.md"
            self.assertEqual(prepare_third_degree("me", archive, [observed], None, 2, task), ["drew", "casey"])
            self.assertIn("third-degree-batch-2.json", task.read_text())
            excluded = base / "inaccessible.txt"
            excluded.write_text("@drew\n")
            self.assertEqual(prepare_third_degree("me", archive, [observed], excluded, 2, task), ["casey"])


if __name__ == "__main__":
    unittest.main()
