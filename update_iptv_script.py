import json
import re
import os
import urllib.request
import urllib.error

def update_iptv():
    # Configuration
    url = "https://raw.githubusercontent.com/zzzz0317/beijing-unicom-iptv/refs/heads/main/iptv-multicast.m3u"
    url_corrected = "https://raw.githubusercontent.com/zzzz0317/beijing-unicom-iptv/main/iptv-multicast.m3u"
    
    output_file = "iptv.m3u"
    json_file = os.path.join("capture", "channelAcquire.txt")
    
    # Download M3U using urllib
    print(f"Downloading M3U from {url_corrected}...")
    content = ""
    try:
        with urllib.request.urlopen(url_corrected) as response:
            content = response.read().decode('utf-8')
    except urllib.error.HTTPError as e:
        if e.code == 404:
             print(f"Corrected URL failed not found, trying user provided path: {url}")
             try:
                with urllib.request.urlopen(url) as response:
                    content = response.read().decode('utf-8')
             except Exception as e2:
                 print(f"Failed to download from secondary URL: {e2}")
        else:
            print(f"Failed to download M3U: {e}")
            
    except Exception as e:
        print(f"Failed to download M3U: {e}")

    if not content:
        # Fallback to reading local file if download fails and it exists
        if os.path.exists("iptv-multicast.m3u"):
            print("Falling back to local iptv-multicast.m3u")
            with open("iptv-multicast.m3u", "r", encoding="utf-8") as f:
                content = f.read()
        else:
            print("No local file found to fallback to.")
            return

    # Load JSON
    print(f"Loading channel info from {json_file}...")
    try:
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Flatten extracted channels into a dict: Name -> TimeShiftURL
            channels_info = {}
            if "channleInfoStruct" in data:
                for ch in data["channleInfoStruct"]:
                    name = ch.get("channelName")
                    ts_url = ch.get("timeShiftURL")
                    if name and ts_url:
                         channels_info[name] = ts_url
    except Exception as e:
        print(f"Failed to read JSON: {e}")
        return

    lines = content.splitlines()
    new_lines = []
    
    # Process lines
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
            
        if line.startswith("#EXTINF"):
            # Add empty line before #EXTINF (unless it's the very first line)
            if new_lines: 
                new_lines.append("")
            
            # Extract channel name for matching (tvg-name or last part)
            # Strategy: Try tvg-name, then zz-raw-name, then comma name
            match_name = None
            
            # 1. tvg-name
            tvg_name_match = re.search(r'tvg-name="([^"]+)"', line)
            if tvg_name_match:
                name_candidate = tvg_name_match.group(1)
                if name_candidate in channels_info:
                    match_name = name_candidate
            
            # 2. zz-raw-name (if not matched yet)
            if not match_name:
                raw_name_match = re.search(r'zz-raw-name="([^"]+)"', line)
                if raw_name_match:
                    name_candidate = raw_name_match.group(1)
                    if name_candidate in channels_info:
                        match_name = name_candidate

            # 3. Comma name (if not matched yet)
            if not match_name:
                parts = line.split(",")
                if len(parts) > 1:
                    name_candidate = parts[-1].strip()
                    if name_candidate in channels_info:
                        match_name = name_candidate
            
            # Update catchup-source if matching channel found
            if match_name:
                ts_url = channels_info[match_name]
                new_catchup = f'catchup-source="{ts_url}?playseek=${{(b)yyyyMMddHHmmss}}-${{(e)yyyyMMddHHmmss}}"'
                
                # Check if catchup-source exists
                if 'catchup-source="' in line:
                    # Replace existing
                    line = re.sub(r'catchup-source="[^"]+"', new_catchup, line)
                else:
                    # Insert before comma
                    comma_index = line.rfind(',')
                    if comma_index != -1:
                        line = line[:comma_index] + " " + new_catchup + line[comma_index:]
                    else:
                        line += " " + new_catchup

            new_lines.append(line)
            
        elif "rtp://" in line:
            # Replace rtp:// with http proxy
            line = line.replace("rtp://", "http://192.168.11.1:5140/rtp/")
            new_lines.append(line)
        else:
            new_lines.append(line)

    # Write output
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(new_lines))
    print(f"Created {output_file}")

if __name__ == "__main__":
    update_iptv()
