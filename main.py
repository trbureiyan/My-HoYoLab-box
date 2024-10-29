# @author https://github.com/jilliangmeehan

import requests
import os
import json

def get_data_from_hoyolab(hoyo_uid, hoyo_token, hoyo_tmid):
    headers = {
        'x-rpc-language': 'en-us',
        'Cookie': f'ltoken_v2={hoyo_token}; ltmid_v2={hoyo_tmid};'
    }

    url = f'https://bbs-api-os.hoyolab.com/game_record/card/wapi/getGameRecordCard?uid={hoyo_uid}'
    
    response = requests.get(url=url, headers=headers)
    if response.status_code != 200:
        print(f"Error: API request failed with status code {response.status_code}")
        return None

    try:
        json_data = response.json()
        # Print the entire response for debugging
        print("API Response:")
        print(json.dumps(json_data, indent=2))
    except json.JSONDecodeError:
        print("Error: Failed to decode JSON response")
        return None

    if 'data' not in json_data or 'list' not in json_data['data']:
        print("Error: Unexpected JSON structure")
        return None

    return json_data['data']['list']

def format_game_stats(game):
    game_id = game['game_id']
    game_name = game['game_name']
    level = game['level']
    
    print(f"Formatting stats for {game_name}:")
    print(json.dumps(game, indent=2))
    
    stats = {item['name']: item['value'] for item in game['data']}
    
    def get_stat(keys):
        for key in keys:
            if key in stats:
                return stats[key]
        return "N/A"

    if game_id == 2:  # Genshin Impact
        return f"🎮 {game_name}\n"\
               f"⚔️ Lv.{level}\n"\
               f"🕹️ Active Days: {get_stat(['Active Days', 'Days Active', '活跃天数'])}\n"\
               f"🤝 Characters: {get_stat(['Characters', 'Characters Obtained', '获得角色数'])}\n"\
               f"🏆 Achievements: {get_stat(['Achievements', 'Achievements Unlocked', '成就达成数'])}\n"\
               f"🌟 Spiral Abyss: {get_stat(['Spiral Abyss', 'Spiral Abyss Progress', '深境螺旋'])}\n"
    
    else:  # Generic format for unknown games
        return f"🎮 {game_name}\n"\
               f"⚔️ Lv.{level}\n"\
               + "\n".join(f"{key}: {value}" for key, value in stats.items())

def update_gist(gh_api_url, gh_token, gist_id, hoyo_data):
    if not hoyo_data:
        print("Error: No data to update gist")
        return

    str_hoyo_data = ""
    for game in hoyo_data:
        str_hoyo_data += format_game_stats(game) + "\n"

    data = {
        'description': '🎮 HoYoverse gameplay stats',
        'files': {'🎮 HoYoverse gameplay stats': {'content': str_hoyo_data}}
    }

    try:
        response = requests.patch(
            url=f'{gh_api_url}/gists/{gist_id}',
            headers={
                'Authorization': f'token {gh_token}',
                'Accept': 'application/json'
            },
            json=data
        )
        response.raise_for_status()
        print("Gist updated successfully!")
    except requests.exceptions.RequestException as e:
        print(f"Error updating gist: {e}")

if __name__ == '__main__':
    hoyo_uid = os.environ['HOYO_UID']
    hoyo_token = os.environ['HOYO_TOKEN']
    hoyo_tmid = os.environ['HOYO_TMID']
    gh_token = os.environ['GH_TOKEN']
    gist_id = os.environ['GIST_ID']
    gh_api_url = 'https://api.github.com'

    hoyo_data = get_data_from_hoyolab(hoyo_uid, hoyo_token, hoyo_tmid)
    if hoyo_data:
        update_gist(gh_api_url, gh_token, gist_id, hoyo_data)
    else:
        print("Failed to retrieve data from HoYoLab")
