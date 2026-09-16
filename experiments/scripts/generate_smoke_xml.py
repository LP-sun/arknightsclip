import os

def generate_resolve_smoke_xml():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    pen_png = os.path.abspath(os.path.join(base_dir, "experiments", "pen_renderer", "outputs", "exusiai_test.png"))
    react_png = os.path.abspath(os.path.join(base_dir, "experiments", "react_renderer", "outputs", "exusiai_test.png"))
    out_xml = os.path.abspath(os.path.join(base_dir, "experiments", "react_renderer", "outputs", "resolve_smoke_timeline.xml"))

    pen_url = "file://localhost/" + pen_png.replace('\\', '/')
    react_url = "file://localhost/" + react_png.replace('\\', '/')

    xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE xmeml>
<xmeml version="5">
    <sequence>
        <name>Renderer_Smoke_Test_Pen_vs_React</name>
        <duration>240</duration>
        <rate>
            <timebase>24</timebase>
            <ntsc>FALSE</ntsc>
        </rate>
        <media>
            <video>
                <format>
                    <samplecharacteristics>
                        <width>1920</width>
                        <height>1080</height>
                        <pixelaspectratio>square</pixelaspectratio>
                        <rate>
                            <timebase>24</timebase>
                            <ntsc>FALSE</ntsc>
                        </rate>
                    </samplecharacteristics>
                </format>
                <!-- Track 1: Pen.dev Render (0 - 5s) -->
                <track>
                    <clipitem id="clipitem-pen">
                        <name>Pen_Exusiai_Test</name>
                        <duration>120</duration>
                        <rate>
                            <timebase>24</timebase>
                            <ntsc>FALSE</ntsc>
                        </rate>
                        <start>0</start>
                        <end>120</end>
                        <in>0</in>
                        <out>120</out>
                        <file id="file-pen">
                            <name>exusiai_test.png</name>
                            <pathurl>{pen_url}</pathurl>
                            <rate>
                                <timebase>24</timebase>
                                <ntsc>FALSE</ntsc>
                            </rate>
                            <duration>120</duration>
                            <media>
                                <video>
                                    <samplecharacteristics>
                                        <width>1920</width>
                                        <height>1080</height>
                                    </samplecharacteristics>
                                </video>
                            </media>
                        </file>
                    </clipitem>
                    <!-- Track 1 Cont: React/CSS Render (5 - 10s) -->
                    <clipitem id="clipitem-react">
                        <name>React_Exusiai_Test</name>
                        <duration>120</duration>
                        <rate>
                            <timebase>24</timebase>
                            <ntsc>FALSE</ntsc>
                        </rate>
                        <start>120</start>
                        <end>240</end>
                        <in>0</in>
                        <out>120</out>
                        <file id="file-react">
                            <name>exusiai_test.png</name>
                            <pathurl>{react_url}</pathurl>
                            <rate>
                                <timebase>24</timebase>
                                <ntsc>FALSE</ntsc>
                            </rate>
                            <duration>120</duration>
                            <media>
                                <video>
                                    <samplecharacteristics>
                                        <width>1920</width>
                                        <height>1080</height>
                                    </samplecharacteristics>
                                </video>
                            </media>
                        </file>
                    </clipitem>
                </track>
            </video>
        </media>
    </sequence>
</xmeml>
"""
    with open(out_xml, "w", encoding="utf-8") as f:
        f.write(xml_content)
    print(f"成功生成 Resolve Smoke Test XML: {out_xml}")

if __name__ == "__main__":
    generate_resolve_smoke_xml()
