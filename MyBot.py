#!/usr/bin/env python3
# Python 3.6

# Import the Halite SDK, which will let you interact with the game.
import hlt
import random
import time
import numpy as np
# This library contains constant values.
from hlt import constants
from scipy.optimize import linear_sum_assignment

from hlt.positionals import Position
# This library contains direction metadata to better interface with the game.
from hlt.positionals import Direction
import time

# This library allows you to generate random numbers.


# Logging allows you to save messages for yourself. This is required because the regular STDOUT
#   (print statements) are reserved for the engine-bot communication.
import logging
""" <<<Game Begin>>> """
#This is a constant that weights the value of distance when assigning target halite cells

dist_cost = 0.1
ship_dist_cost = 0.3
slow_factor = 2.0
inspiration_value = 2.0
avoidance_value = 0.4
map_refresh_rate = 3
max_ships = 80
congestion_factor = 1
homebias = 0.3

positions = {}
other_ships = []

class Boat:
    def __init__(self, shipclass, turn):
        self.shipclass = ship
        self.homeflag = False
        self.turn = turn
        self.individual_map = {}
        self.sums = []
        self.target = Position(0,0)
        self.shipmap()

    def time_to_destination(self, source, destination):
        result = game_map.get_unsafe_moves(source, destination)
        dir = []
        cost = 0
        while result:
            n=0
            tile_cost = game_map[source.directional_offset(result[0])].halite_amount
            while tile_cost >= 50:
                tile_cost = tile_cost/2
                n+=1
            if n >= 1:
                cost += n
            source = source.directional_offset(result[0])
            dir.append(result[0])
            result = game_map.get_unsafe_moves(source, destination)
        return (len(dir) + cost)*slow_factor




    def head_home(self):
        if self.time_to_destination(self.shipclass.position, shipyard_pos) >= constants.MAX_TURNS - game.turn_number:
            self.homeflag = True
            self.target = shipyard_pos

    def shipmap(self):
        self.sums = []
        for key in weight_map:
            dist = game_map.calculate_distance(weight_map[key], self.shipclass.position)
            dist_weight = dist*ship_dist_cost+1
            if weight_map[key] == shipyard_pos:
                weight_sum = self.shipclass.halite_amount*key*homebias
            else:
                weight_sum = key/(dist_weight)
            self.individual_map[weight_sum] = weight_map[key]
            self.sums.append(weight_sum)
        self.sums.sort(reverse=True)
        self.target = self.individual_map[self.sums.pop(0)]

def check_for_my_ships(pos):
    shipsum = 0
    for ship in positions:
        if ship in pos.get_surrounding_cardinals():
            shipsum +=1

    return shipsum

def check_for_enemy_ships(pos):
    shipsum = 0
    for ship in other_ships:
        if ship in pos.get_surrounding_cardinals():
            shipsum +=1
    return shipsum


def generate_map():
    weight_map = {}
    sums = []
    for x in range(0,game_map.width-1):
        for y in range(0, game_map.height-1):
            pos = Position(x,y)
            myshipsum = check_for_my_ships(pos)
            enemyshipsum = check_for_enemy_ships(pos)
            if 1<enemyshipsum<3:
                inspiration = inspiration_value
            else:
                inspiration = avoidance_value
            if pos == shipyard_pos:
                sum = 1
            else:
                sum = game_map[pos].halite_amount
            dist = game_map.calculate_distance(shipyard_pos, pos)
            dist_weight = dist*dist_cost+1
            weight_sum = sum*inspiration/(dist_weight*(myshipsum*congestion_factor+1))
            while weight_sum in weight_map:
                weight_sum += 0.001
            weight_map[weight_sum] = pos

    return weight_map


def safe_square():
    pass

def can_move(ship):
    if ship.halite_amount >= 0.1*game_map[ship.position].halite_amount:
        return True
    else:
        return False


def naive_random(ship1, destination1):
    global ships_in_yard
    global staying
    global prefs_list
    dir = game_map.get_unsafe_moves(ship1.position, destination1)
    directions = Direction.get_all_cardinals()
    prefs = []
    if destination1 == ship1.position or not can_move(ship1):
        prefs = [ship1.position]
        staying[ship1] = prefs
    else:
        for i in dir:
            prefs.append(i)
            directions.remove(i)
        if ship1.position == shipyard_pos and (not ship_dict[ship1].homeflag):

            for i in directions:
                prefs.append(i)
            prefs.append((0,0))
            ships_in_yard[ship1] = prefs
        else:
            prefs.append((0,0))
            for i in directions:
                prefs.append(i)
            prefs_list[ship1] = prefs


# This game object contains the initial game state.
game = hlt.Game()
# At this point "game" variable is populated with initial map data.
# This is a good place to do computationally expensive start-up pre-processing.
# As soon as you call "ready" function below, the 2 second per turn timer will start.
game_map = game.game_map
shipyard_pos = game.me.shipyard.position
weight_map = generate_map()



game.ready("HydraulicSheep")

# Now that your bot is initialized, save a message to yourself in the log file with some important information.
#   Here, you log here your id, which you can always fetch from the game object by using my_id.
logging.info("Successfully created bot! My Player ID is {}.".format(game.my_id))

""" <<<Game Loop>>> """
ship_dict = {}
n=0
while True:
    positions = {}
    other_ships = []
    timer = 0
    starttime = time.time()
    staying = {}
    ships_in_yard = {}
    prefs_list = {}
    # This loop handles each turn of the game. The game object changes every turn, and you refresh that state by
    #   running update_frame().
    game.update_frame()
    # You extract player metadata and the updated map metadata here for convenience.
    me = game.me
    game_map = game.game_map
    timer = time.time()

    weight_map = generate_map()

    timer = time.time() - timer
    logging.debug("MAP GENERATION: "+ str(timer))

    timer = time.time()

    for player in game.players:
        if not player == me.id:
            for ship in game.players[player].get_ships():
                other_ships.append(ship.position)

    timer = time.time() - timer
    logging.debug("POSITION CATALOGUING: "+ str(timer))
    timer = time.time()
    for ship in me.get_ships():
        positions[ship.position] = ship
        if ship not in ship_dict:
            logging.debug("SHIP ID: "+ str(ship.id))
            ship_dict[ship] = Boat(ship,ship.id)
        elif game_map[ship_dict[ship].target].halite_amount < constants.MAX_HALITE / 20 and not ship_dict[ship].homeflag:
            logging.debug("PREPARING SHIPMAP (TOTAL TIME): "+ str(time.time()-starttime))
            ship_dict[ship].shipmap()
        ship_dict[ship].head_home()
        logging.debug("PROCESSED SHIP: "+ str(ship))

    timer = time.time() - timer
    logging.debug("NEW SHIPS AND PLANNING: "+ str(timer))

    timer = time.time()
    for ship in me.get_ships():
        if (ship_dict[ship].turn + n)%map_refresh_rate  == 0:
            if not ship_dict[ship].homeflag:
                ship_dict[ship].shipmap()
    timer = time.time() - timer

    logging.debug("REFRESHING SHIP MAPS: "+ str(timer))

    # Generates a value map each cycle

    # A command queue holds all the commands you will run this turn. You build this list up and submit it at the
    #   end of the turn.
    command_queue = []

    timer = time.time()
    for ship in me.get_ships():

        # For each of your ships, move randomly if the ship is on a low halite location or the ship is full.
        #   Else, collect halite.

        if ship.halite_amount > 0.8*constants.MAX_HALITE and can_move(ship):
            naive_random(ship, shipyard_pos)
        elif game_map[ship.position].halite_amount < constants.MAX_HALITE / 20 and can_move(ship):
            naive_random(ship, ship_dict[ship].target)
        else:
            naive_random(ship, ship.position)


        game_map[ship.position].ship = None
    #Combats Shipyard blocking strategies.

    game_map[shipyard_pos].ship = None

    timer = time.time() - timer
    logging.debug("PLANNING MOVES: "+ str(timer))
    timer = time.time()
    for key in staying:
        game_map[staying[key][0]].mark_unsafe(key)
    timer = time.time() - timer
    logging.debug("SHIPS STANDING STILL: "+ str(timer))
    timer = time.time()
    while ships_in_yard:
        for key in dict(ships_in_yard):
            if not game_map[key.position.directional_offset(ships_in_yard[key][0])].is_occupied:
                command_queue.append(key.move(ships_in_yard[key][0]))
                game_map[key.position.directional_offset(ships_in_yard[key][0])].mark_unsafe(key)
                ships_in_yard.pop(key)
            else:
                ships_in_yard[key].pop(0)
    timer = time.time() - timer
    logging.debug("SHIPS IN YARD: "+ str(timer))
    timer = time.time()
    pains = {}
    while prefs_list:
        copy = dict(prefs_list)
        for key in copy:
            if not game_map[key.position.directional_offset(prefs_list[key][0])].is_occupied:
                if not key.position.directional_offset(prefs_list[key][0]) in positions:
                    command_queue.append(key.move(prefs_list[key][0]))
                    game_map[key.position.directional_offset(prefs_list[key][0])].mark_unsafe(key)
                    del prefs_list[key]
                else:
                    pains[key] = prefs_list.pop(key)
            elif ship_dict[key].homeflag and key.position.directional_offset(prefs_list[key][0]) == shipyard_pos:
                command_queue.append(key.move(prefs_list[key][0]))
                del prefs_list[key]
            else:
                prefs_list[key].pop(0)
    timer = time.time() - timer
    logging.debug("PREFS LIST: "+ str(timer))
    timer = time.time()
    if len(pains)==1:
        for key in dict(pains):
            command_queue.append(key.move(pains[key][0]))
            game_map[key.position.directional_offset(pains[key][0])].mark_unsafe(key)
            pains.pop(key)
    timer = time.time() - timer
    logging.debug("1-LENGTH PAINS: "+ str(timer))
    timer = time.time()
    pointslist = {}
    table = []
    headings = {}
    combos = {}
    count = 0
    for key in dict(pains):
        occupiedlist = []
        for x in range(0,len(pains[key])):
            if not game_map[key.position.directional_offset(pains[key][x])].is_occupied:
                if not key.position.directional_offset(pains[key][x]) in headings:
                    headings[key.position.directional_offset(pains[key][x])] = count
                    table.append([])
                    count +=1
                pains[key][x] = key.position.directional_offset(pains[key][x])
            else:
                occupiedlist.append(x)
        occupiedlist.reverse()
        for i in occupiedlist:
            pains[key].pop(i)

    for key in dict(pains):
        for heading in headings:
            if heading in pains[key]:
                table[headings[heading]].append((pains[key].index(heading)+1) ** 2)
                position = len(table[headings[heading]])-1
                combos[(headings[heading],position)] = [key,heading]
            else:
                table[headings[heading]].append(100000)
                position = len(table[headings[heading]])-1
                combos[(headings[heading],position)] = [key,heading]
    timer = time.time() - timer
    logging.debug("ARRANGED INTO TABLE: "+ str(timer))
    timer = time.time()
    if table:
        t = np.array(table)
        t = t.transpose()
        row_ind, col_ind = linear_sum_assignment(t)
        for i in range(0, len(row_ind)):
            selection = combos[(col_ind[i],row_ind[i])]
            directions = Direction.get_all_cardinals() + [Direction.Still]
            for i in directions:
                if selection[0].position.directional_offset(i) == selection[1]:
                    command_queue.append(selection[0].move(i))
                    game_map[selection[1]].mark_unsafe(selection[0])
                    break
    timer = time.time() - timer
    logging.debug("ALGORITHM AND MOVES: "+ str(timer))
    timer = time.time()
    # If the game is in the first 200 turns and you have enough halite, spawn a ship.
    # Don't spawn a ship if you currently have a ship at port, though - the ships will collide.
    if game.turn_number <= 200 and me.halite_amount >= constants.SHIP_COST and not (game_map[me.shipyard].is_occupied or len(ship_dict)>=max_ships):
        command_queue.append(me.shipyard.spawn())
    timer = time.time() - timer
    logging.debug("SPAWNING: "+ str(timer))
    logging.debug("TOTAL TIME: "+ str(time.time() - starttime))
    # Send your moves back to the game environment, ending this turn.
    n +=1
    game.end_turn(command_queue)
