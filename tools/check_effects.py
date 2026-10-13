"""Dev only: effects for checking the scripted pages in a game that is left open.

    python -I tools/check_effects.py            write common/scripted_effects/mod1440_check.txt; a running game
                                                reads it within seconds ("Reloading Database" in error.log)
    python -I tools/check_effects.py --restore  remove it again. The test suite fails while it is there.

Each effect is run from the console with nothing selected: effect mod1440_chk_<name>. They change the game of
the check, which is never saved. What an effect finds out goes to game.log as a line "MOD1440 ...".

They are for a new game as Germany on 1 January 1936, the clean state of tools/Invoke-GameSteps.ps1 -Start;
those named rt56 are for the map of Road to 56, as the United States.
The notes of each phase say which were used for what (wiki/phases/E1-war-diary.md, "Game checks").
"""
import io
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(ROOT, "common", "scripted_effects", "mod1440_check.txt")

EFFECTS = """# CHECK ONLY: written by tools/check_effects.py, removed with --restore.

# ---- events, caused while paused (as Germany on 1 January 1936)

# War on Poland, and on Czechoslovakia.
mod1440_chk_war = {
	declare_war_on = { target = POL type = annex_everything }
}

mod1440_chk_war2 = {
	declare_war_on = { target = CZE type = annex_everything }
}

mod1440_chk_peace = {
	white_peace = POL
}

# Czechoslovakia annexed (needs the war first for a line about it).
mod1440_chk_annex = {
	annex_country = { target = CZE transfer_troops = no }
}

# Denmark made a subject.
mod1440_chk_puppet = {
	puppet = DEN
}

# Niederschlesien lost to Poland and taken back; Danzig taken.
mod1440_chk_state = {
	POL = { set_state_controller = 66 }
	set_state_controller = 66
}

mod1440_chk_state2 = {
	set_state_controller = 85
}

# Brandenburg, the capital's state, lost to Poland and taken back.
mod1440_chk_capital = {
	POL = { set_state_controller = 64 }
	set_state_controller = 64
}

# The copy of who holds each victory point, taken now, with a line in game.log.
mod1440_chk_sync = {
	mod1440_vp_sync = yes
	log = "MOD1440 check: sync, [?mod1440_vp_ctl^num] points, version [?mod1440_vp_ver], first holder [?mod1440_vp_ctl^0.GetName], Berlin [?global.province_controllers^6521.GetName]"
}

# Thorn (5 points): the territory log only
mod1440_chk_vp1 = {
	set_province_controller = 3295
	mod1440_vp_scan = yes
}

# Krakau (20 points): both logs
mod1440_chk_vp2 = {
	set_province_controller = 9427
	mod1440_vp_scan = yes
}

# Breslau (10 points) lost to Poland
mod1440_chk_vp3 = {
	POL = { set_province_controller = 9570 }
	mod1440_vp_scan = yes
}

# A promotion and a skill level for the third general of the game's list, and a general made by effect.
mod1440_chk_officers = {
	set_temp_variable = { c_g = army_leaders^2 }
	var:c_g = {
		promote_leader = yes
		add_skill_level = 1
	}
	create_corps_commander = {
		name = "Check General"
		skill = 2
		attack_skill = 2
		defense_skill = 2
		planning_skill = 1
		logistics_skill = 1
	}
}

# A general made by create_corps_commander: he has a number, and no portrait of his own.
mod1440_chk_gen = {
	create_corps_commander = {
		name = "Check General"
		skill = 1
		attack_skill = 1
		defense_skill = 1
		planning_skill = 1
		logistics_skill = 1
	}
}

# Two characters without a command get one by effect, the way focuses and most mods add generals: such a
# leader has no number (Engine Facts X66). With a legacy id and without: it makes no difference.
mod1440_chk_by_effect = {
	set_temp_variable = { ref_a = 0 }
	set_temp_variable = { ref_b = 0 }
	every_character = {
		limit = { NOT = { is_corps_commander = yes } NOT = { is_field_marshal = yes } NOT = { is_navy_leader = yes } }
		random_select_amount = 1
		add_corps_commander_role = {
			legacy_id = 77001
			skill = 1
			attack_skill = 1
			defense_skill = 1
			planning_skill = 1
			logistics_skill = 1
		}
		set_temp_variable = { ref_a = THIS }
		save_global_event_target_as = mod1440_chk_a
	}
	every_character = {
		limit = { NOT = { is_corps_commander = yes } NOT = { is_field_marshal = yes } NOT = { is_navy_leader = yes } }
		random_select_amount = 1
		add_corps_commander_role = {
			skill = 1
			attack_skill = 1
			defense_skill = 1
			planning_skill = 1
			logistics_skill = 1
		}
		set_temp_variable = { ref_b = THIS }
		save_global_event_target_as = mod1440_chk_b
	}
	log = "MOD1440 legacy: with id [mod1440_chk_a.GetName] THIS [?ref_a] [?ref_a.GetName] | without [mod1440_chk_b.GetName] THIS [?ref_b] [?ref_b.GetName]"
}

# The fifth general of the game's list retires.
mod1440_chk_retire = {
	set_temp_variable = { c_g = army_leaders^4 }
	var:c_g = { retire = yes }
}

# Four German advisors hired.
mod1440_chk_hire = {
	activate_advisor = konstantin_von_neurath
	activate_advisor = todt
	activate_advisor = werner_von_fritsch_army_chief
	activate_advisor = gerd_von_rundstedt
}

# ---- the rounds the game runs by itself

# The daily round of the Records, now.
mod1440_chk_daily = {
	mod1440_rec_daily = yes
}

# The search for the places of leaders without a number, with what it found in game.log. Two lines with
# the same second mean it took less than one.
mod1440_chk_refs = {
	log = "MOD1440 refs: start"
	mod1440_of_refs = yes
	log = "MOD1440 refs: done, stale [?rf_stale] need [?rf_need] found [?rf_found] moved [?rf_old^num] top [?global.mod1440_ch_top] known [?mod1440_of_known^num] rows [?mod1440_of_rows^num]"
}

# The comparison of the victory points 400 times, between lines of game.log.
mod1440_chk_time = {
	log = "MOD1440 time: start"
	for_loop_effect = {
		start = 0
		end = 200
		value = chk_n
		mod1440_vp_scan = yes
	}
	log = "MOD1440 time: 200 scans done"
	for_loop_effect = {
		start = 0
		end = 200
		value = chk_n
		mod1440_vp_scan = yes
	}
	log = "MOD1440 time: 400 scans done"
}

# ---- a game as something else left it

# As a game saved with the build of 2026-10-12: the logs and the wars without their newer parts.
mod1440_chk_old = {
	clear_array = mod1440_ev_c
	clear_array = mod1440_ev_sc
	clear_array = mod1440_ev_p
	clear_array = mod1440_ev_x
	clear_array = mod1440_tr_c
	clear_array = mod1440_tr_sc
	clear_array = mod1440_tr_p
	clear_array = mod1440_tr_x
	clear_array = mod1440_wr_vpt
	clear_array = mod1440_wr_vpl
	clear_array = mod1440_wo_vpt
	clear_array = mod1440_wo_vpl
	mod1440_chk_sizes = yes
}

# As if the game's list of characters had changed: everybody the mod keeps by his place believes he stood three
# places further on, and so do the lists.
mod1440_chk_shift = {
	set_temp_variable = { sh = 0 }
	every_unit_leader = {
		limit = { check_variable = { mod1440_ch_at > 0 } }
		add_to_variable = { mod1440_ch_at = 0.00003 }
		add_to_temp_variable = { sh = 1 }
	}
	for_loop_effect = {
		start = 0
		end = mod1440_of_known^num
		value = sh_i
		if = { limit = { check_variable = { mod1440_of_known^sh_i > 5368 } } add_to_variable = { mod1440_of_known^sh_i = 0.00003 } }
	}
	for_loop_effect = {
		start = 0
		end = mod1440_ev_a^num
		value = sh_i
		if = { limit = { check_variable = { mod1440_ev_sa^sh_i = 1 } check_variable = { mod1440_ev_a^sh_i > 5368 } } add_to_variable = { mod1440_ev_a^sh_i = 0.00003 } }
	}
	if = { limit = { check_variable = { mod1440_of_sel > 5368 } } add_to_variable = { mod1440_of_sel = 0.00003 } }
	add_to_variable = { global.mod1440_ch_top = 0.00003 }
	log = "MOD1440 shift: [?sh] leaders moved, top [?global.mod1440_ch_top]"
}

# ---- with the map of Road to 56 (the playset of 2026-10-13), as the United States after the console's "tag USA"

# Which map the mod takes the loaded game for: its number of states, and the table (0 is the game's own).
mod1440_chk_map = {
	mod1440_vp_map = yes
	log = "MOD1440 check: [?vp_states] states, table [?vp_map], [?mod1440_vp_ctl^num] points copied, version [?mod1440_vp_ver]"
}

# War on Mexico.
mod1440_chk_rt56_war = {
	declare_war_on = { target = MEX type = annex_everything }
}

# Monterrey: 20 points in Tamaulipas on that map (the game's own: 10 points, and another state). Both logs.
mod1440_chk_rt56_vp1 = {
	set_province_controller = 12835
	mod1440_vp_scan = yes
}

# Tampico: a point only that map has.
mod1440_chk_rt56_vp2 = {
	set_province_controller = 5021
	mod1440_vp_scan = yes
}

# Eureka in California, a point only that map has, lost to Mexico.
mod1440_chk_rt56_vp3 = {
	MEX = { set_province_controller = 610 }
	mod1440_vp_scan = yes
}

# Whether a condition on an idea nobody defined is an error: read error.log after the reload, then run it.
mod1440_chk_idea = {
	if = {
		limit = { has_idea = mod1440_chk_no_such_idea }
		log = "MOD1440 check: an idea nobody defined is held"
	}
	else = {
		log = "MOD1440 check: an idea nobody defined is not held"
	}
}

# ---- numbers into game.log

# Who the game counts as an officer, each way script can ask (the generals another mod adds were missing).
mod1440_chk_leaders = {
	set_temp_variable = { n_arr = army_leaders^num }
	set_temp_variable = { n_nav = navy_leaders^num }
	set_temp_variable = { n_eal = 0 }
	every_army_leader = { add_to_temp_variable = { n_eal = 1 } }
	set_temp_variable = { n_eal_inv = 0 }
	every_army_leader = { include_invisible = yes add_to_temp_variable = { n_eal_inv = 1 } }
	set_temp_variable = { n_enl = 0 }
	every_navy_leader = { add_to_temp_variable = { n_enl = 1 } }
	set_temp_variable = { n_eul = 0 }
	every_unit_leader = { add_to_temp_variable = { n_eul = 1 } }
	set_temp_variable = { n_ech = 0 }
	every_character = { add_to_temp_variable = { n_ech = 1 } }
	set_temp_variable = { n_role = 0 }
	every_character = {
		limit = { OR = { is_corps_commander = yes is_field_marshal = yes is_navy_leader = yes } }
		add_to_temp_variable = { n_role = 1 }
	}
	log = "MOD1440 leaders [GetTag]: army_leaders [?n_arr] navy_leaders [?n_nav] every_army_leader [?n_eal] with invisible [?n_eal_inv] every_navy_leader [?n_enl] every_unit_leader [?n_eul] every_character [?n_ech] with a command [?n_role] known [?mod1440_of_known^num] rows [?mod1440_of_rows^num]"
}

# How long each part of the two logs and of the wars is.
mod1440_chk_sizes = {
	log = "MOD1440 check: sizes ev [?mod1440_ev_date^num]/[?mod1440_ev_c^num]/[?mod1440_ev_sc^num]/[?mod1440_ev_p^num]/[?mod1440_ev_x^num] tr [?mod1440_tr_date^num]/[?mod1440_tr_c^num]/[?mod1440_tr_sc^num]/[?mod1440_tr_p^num]/[?mod1440_tr_x^num] wr [?mod1440_wr_enemy^num]/[?mod1440_wr_vpt^num]/[?mod1440_wr_vpl^num] wo [?mod1440_wo_enemy^num]/[?mod1440_wo_vpt^num]/[?mod1440_wo_vpl^num]"
}

# The Records in numbers.
mod1440_chk_log = {
	log = "MOD1440 check: ev [?mod1440_ev_date^num] tr [?mod1440_tr_date^num] c [?mod1440_tr_c^num] x [?mod1440_tr_x^num] enemies [?mod1440_ev_enemies^num] wr [?mod1440_wr_enemy^num] vpt [?mod1440_wr_vpt^num] wo [?mod1440_wo_enemy^num] sel [?mod1440_wr_sel_kind]/[?mod1440_wr_sel_i] has [?mod1440_wr_c_has] lines [?mod1440_wr_ln_n] view [?mod1440_wd_fam^num] ctl [?mod1440_vp_ctl^num] ver [?mod1440_vp_ver]"
}
"""


def history_months(name, months, years):
    """An effect that fills the arrays of the History page with made-up months, without running time: a rising
    figure, a falling one and a wave, by turns. years: with the year of each month, or without as a game saved
    before 2026-10-12 has them."""
    series = "".join(("\t\tadd_to_array = { mod1440_h_%d = up }\n" if n % 3 == 0 else
                      "\t\tadd_to_array = { mod1440_h_%d = down }\n" if n % 3 == 1 else
                      "\t\tadd_to_array = { mod1440_h_%d = wave }\n") % n for n in range(12))
    forget = "".join("\t\t\tremove_from_array = { array = mod1440_h_%d index = 0 }\n" % n for n in range(12))
    clear = "".join("\tclear_array = mod1440_h_%d\n" % n for n in range(12))
    year = """		set_temp_variable = { mo = t }
		modulo_temp_variable = { mo = 12 }
		set_temp_variable = { yr = t }
		subtract_from_temp_variable = { yr = mo }
		divide_temp_variable = { yr = 12 }
		add_to_temp_variable = { yr = 1936 }
		add_to_array = { mod1440_h_year = yr }
""" if years else ""
    forget_year = "\t\t\tremove_from_array = { array = mod1440_h_year index = 0 }\n" if years else ""
    return """
%s = {
%s	clear_array = mod1440_h_date
	clear_array = mod1440_h_year
	for_loop_effect = {
		start = 0
		end = %d
		value = t
		set_temp_variable = { up = t }
		multiply_temp_variable = { up = t }
		add_to_temp_variable = { up = 9000 }
		set_temp_variable = { down = 130 }
		subtract_from_temp_variable = { down = t }
		set_temp_variable = { wave = t }
		modulo_temp_variable = { wave = 24 }
		add_to_temp_variable = { wave = 10 }
%s		add_to_array = { mod1440_h_date = global.date }
%s		if = {
			limit = { check_variable = { mod1440_h_date^num > 120 } }
%s			remove_from_array = { array = mod1440_h_date index = 0 }
%s		}
	}
	mod1440_h_draw = yes
	log = "MOD1440 check: history filled, [?mod1440_h_date^num] months, [?mod1440_h_0^num] values, [?mod1440_h_year^num] years"
}
""" % (name, clear, months, series, year, forget, forget_year)


# 130 months with years (the oldest ten are forgotten), the same as an older save has them, and seven months
HISTORY = ("\n# ---- the History page: made-up months\n"
           + history_months("mod1440_chk_months", 130, True) + history_months("mod1440_chk_months_old", 130, False)
           + history_months("mod1440_chk_months_few", 7, True))

if __name__ == "__main__":
    if "--restore" in sys.argv:
        if os.path.isfile(PATH):
            os.remove(PATH)
            print("removed", PATH)
    else:
        io.open(PATH, "w", encoding="utf-8", newline="\n").write(EFFECTS + HISTORY)
        print("wrote", PATH)
        # a running game reads the script again when a file under common/scripted_guis has a new time stamp
        folder = os.path.join(ROOT, "common", "scripted_guis")
        now = time.time()
        for name in os.listdir(folder):
            os.utime(os.path.join(folder, name), (now, now))
