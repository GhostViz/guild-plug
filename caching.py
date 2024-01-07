from configs import blizz_conf, redis_conf
import json, datetime, time, random

r = redis_conf.r
api_client = blizz_conf.api_client

def guild_roster_update( region, locale, guild_slug, guild_realm ):
    """Retrieves guild roster information as json output from battle.net's world of warcraft profile api and caches it to redis"""
    guild_info = api_client.wow.profile.get_guild_roster( region, locale, guild_realm, guild_slug )
    now = str( datetime.datetime.utcnow() )

    r.set( guild_slug + "_" + guild_realm + "_roster_last_update", now )
    r.set( guild_slug + "_" + guild_realm, json.dumps( guild_info ) )

    last_update = r.get( guild_slug + "_" + guild_realm + "_roster_last_update" ).decode( 'ascii' )
    return "Guild roster info for " + guild_slug + " on " + guild_realm + " last updated: " + last_update

def character_professions_update( character_realm, character_name, guild_slug, guild_realm  ):
    """Retrieves character profession information as json output from battle.net's world of warcraft profile api and caches it to redis"""
    count = 0
    now = str( datetime.datetime.utcnow() )

    character_professions = api_client.wow.profile.get_character_professions_summary( 'us', 'en_us', character_realm, character_name )

    r.set( guild_slug + "_" + guild_realm + "_" + character_name + "_" + character_realm + "_last_update", now )
    r.set( guild_slug + "_" + guild_realm + "_" + character_name + "_" + character_realm, json.dumps( character_professions ) )

    last_update = r.get( guild_slug + "_" + guild_realm + "_" + character_name + "_" + character_realm + "_last_update" ).decode( 'ascii' )
    return 

def guild_roster_character_professions_update( guild_roster, guild_slug, guild_realm ):
    """Loops through an entire guild roster calling character_professions_update()"""
    count = 0 

    for member in guild_roster:
        now = str( datetime.datetime.utcnow() )
        character_name = member.get( "character" ).get( "name" ).lower()
        character_realm = member.get( "character" ).get( "realm" ).get( "slug" ).lower()

        character_professions_update( character_realm, character_name, guild_slug, guild_realm )

        count += 1

        print( '.', end='', flush=True )

    now = str( datetime.datetime.utcnow() )
    r.set(guild_slug + "_" + guild_realm + "_professions_last_update", now)
    last_update = r.get(guild_slug + "_" + guild_realm + "_professions_last_update").decode( 'ascii' )
    return "Profession cache for " + str( count ) + " members of " + guild_slug + " updated at: " + last_update 

