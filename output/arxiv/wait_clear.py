import time, urllib.request, urllib.error, sys

URL = ("https://export.arxiv.org/api/query?search_query=ti%3A%22world+model%22"
       "+AND+submittedDate%3A%5B202609280000+TO+202610282359%5D"
       "&start=0&max_results=5")

for i in range(20):
    try:
        with urllib.request.urlopen(URL, timeout=30) as r:
            if r.status == 200:
                print("CLEARED after %d probes" % i, flush=True)
                sys.exit(0)
            print("probe %d status=%s" % (i, r.status), flush=True)
    except urllib.error.HTTPError as e:
        print("probe %d http=%s" % (i, e.code), flush=True)
    except Exception as e:
        print("probe %d err=%s" % (i, str(e)[:60]), flush=True)
    time.sleep(30)

print("STILL_LIMITED", flush=True)
sys.exit(1)
