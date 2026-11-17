#!/usr/bin/env python3
"""Self-check for nle.py parsers: python3 test_nle.py"""
import tempfile
from pathlib import Path
from nle import load, summarize

XMEML = """<xmeml version="4"><sequence><duration>300</duration><rate><timebase>30</timebase></rate>
<media><video><format><samplecharacteristics><width>1920</width><height>1080</height></samplecharacteristics></format>
<track>
 <clipitem><name>a.mp4</name><start>0</start><end>90</end><in>0</in><out>90</out></clipitem>
 <clipitem><name>a.mp4</name><start>90</start><end>200</end><in>100</in><out>210</out></clipitem>
 <transitionitem><start>190</start><end>210</end><effect><name>Cross Dissolve</name></effect></transitionitem>
 <clipitem><name>a.mp4</name><start>-1</start><end>300</end><in>220</in><out>310</out></clipitem>
</track>
<track><clipitem><name>screen.mp4</name><start>30</start><end>150</end><in>0</in><out>120</out>
 <filter><effect><name>Basic Motion</name>
  <parameter><parameterid>scale</parameterid><value>30</value></parameter>
  <parameter><parameterid>center</parameterid><value><horiz>0.6</horiz><vert>0.5</vert></value></parameter>
 </effect></filter></clipitem></track>
</video><audio>
<track>
 <clipitem><name>a.mp4</name><start>0</start><end>84</end><in>0</in><out>84</out></clipitem>
 <clipitem><name>a.mp4</name><start>84</start><end>206</end><in>94</in><out>216</out></clipitem>
 <clipitem><name>a.mp4</name><start>206</start><end>300</end><in>226</in><out>320</out></clipitem>
</track>
<track><clipitem><name>whoosh.wav</name><start>88</start><end>100</end><in>0</in><out>12</out></clipitem></track>
</audio></media></sequence></xmeml>"""

FCPXML = """<fcpxml version="1.10"><resources><format id="r1" frameDuration="1/30s" width="1080" height="1920"/></resources>
<library><event><project><sequence format="r1" duration="10s"><spine>
 <asset-clip name="a" offset="0s" start="0s" duration="4s">
   <title lane="1" name="t" offset="1s" duration="2s"><text><text-style ref="ts1">Hello</text-style></text>
     <text-style-def id="ts1"><text-style font="Inter" fontSize="80" fontColor="1 1 1 1"/></text-style-def></title>
   <asset-clip lane="-1" name="music" offset="0s" start="0s" duration="10s"><adjust-volume amount="-20dB"/></asset-clip>
 </asset-clip>
 <transition name="Cross Dissolve" offset="3.5s" duration="1s"/>
 <asset-clip name="a" offset="4s" start="10s" duration="6s" audioStart="9.5s" audioDuration="6.5s">
   <asset-clip lane="1" name="pip" offset="11s" start="10s" duration="3s"><adjust-transform scale="0.3 0.3" position="20 -30"/></asset-clip>
 </asset-clip>
</spine></sequence></project></event></library></fcpxml>"""

with tempfile.TemporaryDirectory() as d:
    x = Path(d) / "a.xml"; x.write_text(XMEML)
    s = summarize(load(x))
    assert s["mainTrack"]["clips"] == 3, s["mainTrack"]
    assert s["transitions"]["names"] == {"Cross Dissolve": 1}
    assert s["overlays"]["pipClips"] == 1 and "scale 30%" in next(iter(s["overlays"]["pipPositions"]))
    assert s["jlCuts"]["jCuts"] == 2, s["jlCuts"]          # audio cut 6 and 4 frames before video
    assert s["audio"]["sfxCount"] == 1

    f = Path(d) / "b.fcpxml"; f.write_text(FCPXML)
    s = summarize(load(f))
    assert s["aspect"] == "9:16" and s["mainTrack"]["clips"] == 2
    assert s["text"]["count"] == 1 and s["text"]["fonts"] == {"Inter": 1}
    assert s["jlCuts"]["jCuts"] == 1, s["jlCuts"]          # audioStart 0.5s before the video
    assert s["audio"]["musicVolumeDb"] == [-20.0], s["audio"]
    assert s["overlays"]["pipClips"] == 1
print("ok")
