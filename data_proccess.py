import json
import dropbox
import pandas as pd
import pickle
import io

token = "xtLHltG_SEAAAAAAAAAADPjsxmboPj-DvkC2sEDYsqa212QpB8t0_X0c_TM6ez25"

dbx = dropbox.Dropbox(token)

list_of_dics = pickle.loads(dbx.files_download("/all_dics_8")[1].content)

#check for empty dictionaries and deletes them
for i in range(2):
    a = len(list_of_dics)

    for idx, i in enumerate(list_of_dics):
        if len(i.keys()) != 28:
            del list_of_dics[idx]
        else:
            pass
    print("{} dicts were deleted".format(a - len(list_of_dics)))
    
    home_team_id_dic = {}
away_team_id_dic = {}


for i in list_of_dics:
    home_team_id_dic[i["home"]["teamId"]] = i["home"]['name']
    away_team_id_dic[i["away"]["teamId"]] = i["away"]['name']

team_id_dic = home_team_id_dic

for v in away_team_id_dic:
    try:
        if away_team_id_dic[v] != home_team_id_dic[v]:
            raise ValueError('TeamID and TeamName differs in the away_team_id_dic and home_team_id_dic at index {}'\
                             .format(v))
    except:
        pass
    if v in home_team_id_dic.keys():
        pass
    else:
        team_id_dic[v] = away_team_id_dic[v]
        
        
player_id_dic = {}
for i in list_of_dics:
    for player_key in i["playerIdNameDictionary"].keys():
        if player_key not in player_id_dic:
            player_id_dic[player_key] = i["playerIdNameDictionary"][player_key]            
    for away_player_key in i["away"]["players"]:
        if away_player_key["playerId"] not in player_id_dic:
            player_id_dic[away_player_key["playerId"]] = away_player_key["name"]
            
            
            
def database_maker(list_of_dics):
    touches = []
    for idx, i in enumerate(list_of_dics):
        for e in i["events"]:
            if e["type"]["displayName"] == 'Pass':
                try:
                    touches.append(
                        {                     
                        "home_team": team_id_dic[e["teamId"]],
                        "Player": player_id_dic[str(e["playerId"])],
                        "Date": int(i["startDate"][:4]) + int(i["startDate"][5:7]) + int(i["startDate"][8:10]),
                        "start_x": e["x"],
                        "start_y": e["y"],
                        "end_x": e["endX"],                
                        "end_y": e["endY"],
                        "Outcome": e["outcomeType"]["displayName"],
                        "Minute": e["minute"]   
                        }
                    )

                except:
                    pass
    return touches

touches = database_maker(list_of_dics)

touch_df = pd.DataFrame(touches)

touch_df = touch_df.assign(Distance = lambda x: ((x.end_x - x.start_x)**2 + (x.end_y - x.start_y)**2)**(1/2))

touch_df.to_pickle("passes.pkl", compression="gzip")

with open("passes.pkl", "rb") as fp:
    dbx.files_upload(fp.read(), "/passes.pkl")