#ifndef PLAYER_H
#define PLAYER_H

#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include "log.h"

#include "tournament.h"	// For tournament_t

#define NAME_MAX_LENGTH 50

#define SKILL_MAX 100
#define SKILL_AVG 80
#define DELTA_SKILL 15


#define MAX_SECONDS_OUTSIDE	20	// Up to 20 seconds before entering for the first time
#define MAX_TIME_RESTING	5000000	// 5 seconds
#define LEAVING_PROB		2	// 2%	Leaving the tournament completelly
#define RESTING_PROB		15	// 15%	Leaving the tournament for a time with distribution ~U(0, MAX_SECONDS_RESTING)
					//	Should be greater than LEAVING_PROB

/* Third checkpoint major update: From now on, as
 * there will only be one player_t for each player
 * process, player_t struct will become a singleton!*/

/* Player structure used to model a player of
 * the tournament. For the time being, each
 * player has name, a skill field which measures 
 * from 0 to SKILL_MAX how good that player is, 
 * and a courtes_played field which counts how 
 * many courtes the player has been in.*/
typedef struct player_ {
	int id;
	char name[NAME_MAX_LENGTH];
	size_t skill;
	size_t matches_played;
	size_t times_kicked;
	bool currently_playing;

	tournament_t* tm;
} player_t;

/* Returns the current player singleton!*/
player_t* player_get_instance();

/* Destroys the current player.*/
void player_destroy();

/* Set the name for the current player.
 * If name is NULL, silently does nothing.*/
void player_set_name(char* name);

/* Returns the skill of the current player.*/
size_t player_get_skill();

/* Returns the name of the current player.*/
char* player_get_name();

/* Make this player play the current set
 * storing their score in the set_score
 * variable. This function should do the
 * following: make this player sleep an
 * amount of time inversely proportional
 * to their skill, and after that, make
 * it add a point to their score. Then,
 * repeat all over.*/
void player_play_set(unsigned long int* set_score);

/* Returns true or false if the player
 * is or not playing.*/
bool player_is_playing();

/* Makes player stop playing.*/
void player_stop_playing();

/* Makes player stop playing.*/
void player_start_playing();

void player_main(unsigned int id, tournament_t* tm);

#endif
