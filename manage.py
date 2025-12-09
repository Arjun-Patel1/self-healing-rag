# manage.py
import argparse
from reindexer import build_index
from monitor import run_monitor_sample
from self_debug_agent import summarize_and_suggest, load_report
from index_manager import list_versions, rollback_to

parser = argparse.ArgumentParser()
parser.add_argument("--reindex", action="store_true")
parser.add_argument("--monitor", action="store_true")
parser.add_argument("--advice", action="store_true")
parser.add_argument("--list-versions", action="store_true")
parser.add_argument("--rollback", type=str, help="rollback to tag")

args = parser.parse_args()
if args.reindex:
    build_index()
if args.monitor:
    run_monitor_sample()
if args.advice:
    from self_debug_agent import load_report, summarize_and_suggest
    r = load_report()
    print(summarize_and_suggest(r))
if args.list_versions:
    print(list_versions())
if args.rollback:
    rollback_to(args.rollback, "vector.index", "metadata.json")
