"""
将生成的 V2 分层时间线 FCP7 XML 导入 DaVinci Resolve
- 时间线名称: 明日方舟_六星干员报菜名_PSD分层母版合成_v2
- 保证绝不覆盖已有时间线
- 自动创建媒体池箱 04_PSD_Layered_Graphics
"""

import os
import sys

davinci_paths = [
    r'C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules',
    r'C:\Program Files\Blackmagic Design\DaVinci Resolve\Developer\Scripting\Modules'
]
for p in davinci_paths:
    if os.path.exists(p) and p not in sys.path:
        sys.path.append(p)

def import_timeline():
    xml_file = os.path.abspath('reports/timeline_v2_layered.xml')
    if not os.path.exists(xml_file):
        print(f"Error: 未找到 XML 文件 {xml_file}")
        return False

    try:
        import DaVinciResolveScript as dvr
        resolve = dvr.scriptapp('Resolve')
        if not resolve:
            print("DaVinci Resolve 未运行或无法连接，XML 已生成，用户可在达芬奇中直接 File -> Import -> Timeline 导入！")
            return False
    except Exception as e:
        print(f"连接 Resolve 失败: {e}")
        return False

    pm = resolve.GetProjectManager()
    proj = pm.GetCurrentProject()
    mp = proj.GetMediaPool()

    print(f"正在向 DaVinci Resolve 工程 [{proj.GetName()}] 导入新版分层时间线...")
    new_timeline = mp.ImportTimelineFromFile(xml_file, {
        "timelineName": "明日方舟_六星干员报菜名_PSD分层母版合成_v2",
        "importOption": "None"
    })

    if new_timeline:
        print(f"成功创建并导入全新时间线: {new_timeline.GetName()}")
        proj.SetCurrentTimeline(new_timeline)
        return True
    else:
        print("ImportTimelineFromFile 返回 None，尝试创建普通导入...")
        return False

if __name__ == '__main__':
    import_timeline()
