import pytest

from brief import news

FEED = """<?xml version="1.0"?><rss><channel>
<item><title>First story</title><link>https://a.test/1</link></item>
<item><title>Have You Seen This? Viral clip</title><link>https://a.test/2</link></item>
<item><title><![CDATA[Second story]]></title><link>https://a.test/3</link></item>
</channel></rss>"""


def test_parses_items_and_skips_viral_clips():
    assert [story["text"] for story in news.parse_feed(FEED, "KSL")] == ["First story", "Second story"]


def test_interleaves_sources_and_stops_at_the_limit():
    one = [{"text": "a1"}, {"text": "a2"}]
    two = [{"text": "b1"}]
    assert [story["text"] for story in news.interleave([one, two], 2)] == ["a1", "b1"]


def test_removes_duplicates_across_feeds():
    assert len(news.interleave([[{"text": "same"}], [{"text": "same"}]], 5)) == 1


def test_rejects_entity_expansion():
    bomb = '<?xml version="1.0"?><!DOCTYPE x [<!ENTITY a "b">]><rss><item><title>&a;</title></item></rss>'
    with pytest.raises(Exception):
        news.parse_feed(bomb, "Bad")
