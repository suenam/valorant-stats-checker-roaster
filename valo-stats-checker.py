import requests
import random

import PySimpleGUI as pg

def valo_stats(region, user, tagline):
    request = requests.get(f"https://api.henrikdev.xyz/valorant/v3/matches/{region}/{user}/{tagline}?filter=competitive")
    data = request.json()
    stats_dict = {}
    for i in range(len(data["data"])): 
        stats_dict[i] = {} 
        stats_dict[i]["map"] = data["data"][i]["metadata"]["map"]
        for player in data["data"][i]["players"]["all_players"]:
            if (player["name"] == user):
                stats_dict[i]["agent"] = player["character"]
                stats_dict[i]["ability_casts"] = {
                    "c_cast": player["ability_casts"]["c_cast"],
                    "q_cast": player["ability_casts"]["q_cast"],
                    "e_cast": player["ability_casts"]["e_cast"],
                    "x_cast": player["ability_casts"]["x_cast"]
                }
                stats_dict[i]["kda"] = {
                    "kills": player["stats"]["kills"],
                    "deaths": player["stats"]["deaths"],
                    "assists": player["stats"]["assists"],
                    "kd_ratio": round(player["stats"]["kills"] / player["stats"]["deaths"], 2)
                }
                stats_dict[i]["damage_made"] = player["damage_made"]
                stats_dict[i]["damage_received"] = player["damage_received"]
                total_shots = (player["stats"]["bodyshots"] + player["stats"]["headshots"] + player["stats"]["legshots"])
                headshot_perc = (player["stats"]["headshots"] / total_shots) * 100
                stats_dict[i]["headshot_perc"] = round(headshot_perc)

    return stats_dict

def highest_kd(stats_dict):
    max = 0.0
    best_map = ""
    best_agent = ""
    for match in stats_dict:
        if stats_dict[match]["kda"]["kd_ratio"] >= max:
            max = stats_dict[match]["kda"]["kd_ratio"]
            best_map = stats_dict[match]["map"]
            best_agent = stats_dict[match]["agent"]        
    kd_map_agent = [max, best_map, best_agent]

    return kd_map_agent

def highest_headshots(stats_dict):
    max = 0
    best_map = ""
    best_agent = ""
    for match in stats_dict:
        if stats_dict[match]["headshot_perc"] >= max:
            max = stats_dict[match]["headshot_perc"]
            best_map = stats_dict[match]["map"]
            best_agent = stats_dict[match]["agent"]
    hs_map_agent = [f"{max}%", best_map, best_agent]

    return hs_map_agent   


# VALO GOOEY STARTS HERE

# Summary Valo Stats Func
def sum_valo_stats(stats_dict): 
    kd_map_agent = highest_kd(stats_dict)
    hs_map_agent = highest_headshots(stats_dict)
    pg.theme("LightGreen3") 
    center_text = [
        [pg.Text("Summary from your recent comp games...\n", font=(15))],
        [pg.Text(f"Your HIGHEST HEADSHOT PERCENTAGE ({hs_map_agent[0]}) was on {hs_map_agent[1]} with {hs_map_agent[2]}")],
        [pg.Text(f"Your HIGHEST KD ({kd_map_agent[0]}) was on {kd_map_agent[1]} with {kd_map_agent[2]}\n")],
        [pg.Button("Back"), pg.Button("View last 5 matches")]
    ]

    layout = [
        [pg.Push(), pg.Column(center_text, element_justification='c'), pg.Push()],
        [pg.VPush()]
    ]

    window = pg.Window("Valorant Stats Checker", layout, size=(550, 200))
    
    while True:
        event, values = window.read()
        if event == pg.WIN_CLOSED or event == "Close":
            break
        elif event == "Back":
            window.close()
            main()
        elif event == "View last 5 matches":
            window.close()
            match_table(stats_dict)
    
    window.close()


# Table of Matches Func
def match_table(stats_dict): 
    match_info_arr = []
    for i in range(5):
        match_stats = [
            stats_dict[i]["map"],
            stats_dict[i]["agent"],
            stats_dict[i]["kda"]["kills"], 
            stats_dict[i]["kda"]["deaths"], 
            stats_dict[i]["kda"]["assists"]
        ]
        match_info_arr.append(match_stats)

    headings = ["Map", "Agent", "Kills", "Deaths", "Assists"]

    layout = [
        [pg.Table(values=match_info_arr,
        headings=headings,
        max_col_width=35,
        auto_size_columns=True,
        num_rows=5,
        row_height=35,
        enable_events=True,
        key="-MATCH_TABLE-")
        ],
        [pg.Button("Return to stats summary")]
    ]

    window = pg.Window("Valorant Stats Checker", layout)

    while True:
        event, values = window.read()
        if event == pg.WIN_CLOSED:
            break
        elif event == "-MATCH_TABLE-": 
            row_index = values["-MATCH_TABLE-"][0]
            match_details(stats_dict[row_index])
        elif event == "Return to stats summary":
            window.close()
            sum_valo_stats(stats_dict)

    window.close()


# Match Details Func
def match_details(match):
    pg.theme("LightGreen3")
    layout = [
        [pg.Push(), pg.Text("Match Details\n", font=(15)), pg.Push()],
        [pg.Text(f"MAP: {match['map']}")],
        [pg.Text(f"AGENT: {match['agent']}")],
        [pg.Text(f"KDA: {match['kda']['kills']}/{match['kda']['deaths']}/{match['kda']['assists']}")],
        [pg.Text(f"DAMAGE MADE: {match['damage_made']}")],
        [pg.Text(f"DAMAGE RECEIVED: {match['damage_received']}")],
        [pg.Text(f"HEADSHOT PERCENTAGE: {match['headshot_perc']}")],
        [pg.Text(f"AVERAGE KD: {match['kda']['kd_ratio']}")],
        [pg.Text(roast_func(match))],
        [pg.Push(), pg.Button("Ok"), pg.Push()]

    ]

    window = pg.Window("Valorant Stats Checker", layout)

    while True:
        event, values = window.read()
        if event == pg.WIN_CLOSED:
            break
        elif event == "Ok":
            window.close()
    
    window.close()


# Roast Func
def roast_func(match):
    # flash_agents = ["Phoenix", "Breach", "Kay"]
    roast_arr = []
    if match["damage_received"]-1000 > match["damage_made"]:
        roast_arr.append("Damn, were you afk the whole match?")
    if match["kda"]["kd_ratio"] < 1.0:
        roast_arr.append("You didn't even go positive...")
        roast_arr.append("Maybe it's time to hit the range...")
        roast_arr.append("Aimlabs is free.")
        roast_arr.append("New to the game?")
        roast_arr.append("Drawing an outline?")
    if match["headshot_perc"] < 15:
        roast_arr.append("You know you're supposed to aim for the head right?")
        roast_arr.append("Bodyshot Andy.")
        roast_arr.append("Why is your crosshair sweeping the floor?")
    if match["kda"]["kills"]-11 > match["kda"]["assists"]:
        roast_arr.append("Suggestion: stop baiting your team.")
        if match["agent"] == "Sage" or match["agent"] == "Skye":
            roast_arr.append("PLEASE use your heal.")
    if match["agent"] == "Cypher":
        roast_arr.append("You got your Tiktok setups ready?")
        roast_arr.append("Rat gameplay.")
        roast_arr.append("Site POV.")
    if match["agent"] == "Viper":
        roast_arr.append("Lineup Larry.")
    if match["agent"] == "Phoenix" or match["agent"] == "Breach":
        roast_arr.append("You know you're supposed to flash the ENEMY team right?")
    if match["agent"] == "Chamber":
        roast_arr.append("You want to play? Let's play (nerd emoji)")
    if match["agent"] == "Jett":
        roast_arr.append("No pocket sage?")
    roast_arr.append("Please go touch some grass.")
    roast_arr.append("No bitches? :3")
    roast_arr.append("'Pushing C?' How about you C some bitches?")
    roast_arr.append("Are you an ION phantom? 'Cause ION want you.")
    roast_arr.append("Literally trolling (skull emoji x7)")
    roast_arr.append("That's crazy.")

    roast = random.choice(roast_arr)

    return roast

# MAIN
def main():
    pg.theme("LightGreen3")
    layout = [ 
        [pg.Text("Return your stats based on your last 5 comp matches!")],
        [pg.Text("User: ", size=(4, 1)), pg.InputText()],
        [pg.Text("Tag: ", size=(4, 1)), pg.InputText()],
        [   
            pg.Text("Region: "),
            pg.Combo(["na", "eu", "ap", "kr"])
        ],
        [
            pg.Button("Ok"),
            pg.Button("Close")
        ]
    ]

    # Window
    window = pg.Window("Valorant Stats Checker", layout)

    # Event loop
    while True:
        event, values = window.read()
        if event == pg.WIN_CLOSED or event == "Close":
            break
        elif event == "Ok":
            user = values[0]
            tagline = values[1]
            region = values[2]
            stats_dict = valo_stats(region, user, tagline)
            window.close()
            sum_valo_stats(stats_dict) 

    # Close window
    window.close()

main()

