from configs import blizz_conf, redis_conf
import json, datetime, time, random
import pprint

r = redis_conf.r
api_client = blizz_conf.api_client

pp = pprint.PrettyPrinter(indent=4)

region = 'us'
locale = 'en_US'

professions_info = json.dumps( api_client.wow.game_data.get_professions_index( region, locale ) )

r.set("game-data: raw: professions", professions_info)
pp.pprint(professions_info)
professions = json.loads( r.get("game-data: raw: professions") ).get("professions")

for profession in professions:
    profession_id = profession.get("id")
    profession = profession.get("name")
    try:
        profession_list_path = "game-data: professions-list"

        if redis_conf.r.get(profession_list_path):
            if profession in redis_conf.r.get(profession_list_path):
                print (profession + " already present in professions list.")
            else:
                redis_conf.r.append(profession_list_path, profession + ",")  
                print (profession + " added to professions list.")
        else:
            redis_conf.r.set(profession_list_path, profession + ",")
            print (profession + " added to newly created professions list.")

        profession_info_path =  "game-data: professions: " + profession.lower()
        redis_conf.r.set(profession_info_path, '{ "name": "' + profession + '", "id": ' + str(profession_id) + ' }')

        blizz_profession = json.dumps( api_client.wow.game_data.get_profession( region, locale, profession_id ) )
        r.set("game-data: raw: professions: " + profession.lower() , blizz_profession)
        profession_tiers = json.loads(r.get("game-data: raw: professions: " + profession.lower()) ).get("skill_tiers")
        for tier in profession_tiers:
            tier_name = tier.get("name")
            tier_id = tier.get("id")
            print(profession + " " + str(profession_id) + " - " + tier_name + " " + str(tier_id))
            blizz_profession_tier = json.dumps( api_client.wow.game_data.get_profession_skill_tier( region, locale, profession_id, tier_id ) )
            r.set("game-data: raw: professions: " + profession.lower() + ": " + tier_name.lower(), blizz_profession_tier)
            all_recipes_list_path = "game-data: recipes-list"
            profession_recipes_list_path = "game-data: " + profession.lower() + ": " + "recipes-list"

            recipe_categories = json.loads( ( r.get( "game-data: raw: professions: " + profession.lower() + ": " + tier_name.lower() ) ) ).get("categories")
            for category in recipe_categories:
                recipes = category.get("recipes")

                for recipe in recipes:
                    recipe_name = recipe.get("name")

                    if redis_conf.r.get(all_recipes_list_path):
                        if recipe_name in redis_conf.r.get(all_recipes_list_path):
                            print (recipe_name + " already present in all recipe list.")
                        else:
                            redis_conf.r.append(all_recipes_list_path, recipe_name + ",")  
                            print (recipe_name + " added to all recipe list.")
                    else:
                        redis_conf.r.set(all_recipes_list_path, recipe_name + ",")
                        print (recipe_name + " added to newly created all recipe list.")

                    if redis_conf.r.get(profession_recipes_list_path):
                        if recipe_name in redis_conf.r.get(profession_recipes_list_path):
                            print (recipe_name + " already present in " + profession + " recipe list.")
                        else:
                            redis_conf.r.append(profession_recipes_list_path, recipe_name + ",")  
                            print (recipe_name + " added to " + profession + " list.")
                    else:
                        redis_conf.r.set(profession_recipes_list_path, recipe_name + ",")
                        print (recipe_name + " added to newly created " + profession + " recipe list.")
    except:
        print("Error with " + profession + ".")
