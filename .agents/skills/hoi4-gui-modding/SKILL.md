---
name: hoi4-gui-modding
description: >-
  Provides syntax rules, layout architectures, coordinate standards, dropdown specifications,
  and templates for modding Hearts of Iron IV (Clausewitz engine) graphical user interfaces
  (.gui, .gfx, and scripted_guis). Use when creating, editing, positioning, or troubleshooting
  custom windows, buttons, dropdown menus, HUD extensions, or dynamic UI logic.
---

# Hearts of Iron IV GUI Modding Skill

This skill provides full technical specifications, structural conventions, and best practices for creating and debugging user interfaces in Hearts of Iron IV (HOI4).

## 1. Directory Structure & File Roles

All GUI modifications live across four coordinated mod folders:

```text
my_mod/
├── interface/
│   ├── custom_mod_ui.gfx            # Sprite declarations, texture bindings, frame counts
│   └── custom_mod_ui.gui            # Visual layout, coordinate anchors, containers, widgets
├── common/
│   └── scripted_guis/
│       └── custom_gui_logic.txt     # Triggers, scopes, button effects, dynamic lists
└── localisation/
    └── english/
        └── custom_gui_l_english.yml # Text keys, tooltips (MUST be UTF-8 with BOM)
```

---

## 2. Graphic Declarations (`interface/*.gfx`)

Every image, button frame, or tiled background must be registered as a `spriteType` inside a `spriteTypes` block before being referenced in `.gui` files.

### Syntax Standards

```pdx
spriteTypes = {
    # 1. Standard Static Image
    spriteType = {
        name = "GFX_custom_menu_bg"
        texturefile = "gfx/interface/custom_menu_bg.dds"
    }

    # 2. Multi-state Button or Animated Icon
    # noOfFrames: 1 = Static, 2 = Checkbox/toggle, 3 = Standard button (Normal, Pressed, Disabled)
    spriteType = {
        name = "GFX_custom_button"
        texturefile = "gfx/interface/custom_button.dds"
        noOfFrames = 3
    }

    # 3. Nine-Slice Resizable Window Tile
    corneredTileSpriteType = {
        name = "GFX_custom_tiled_window"
        size = { x = 190 y = 190 }
        textureFile = "gfx/interface/tiles/tiled_bg.dds"
        borderSize = { x = 64 y = 64 }
        tilingCenter = yes
    }
}
```

* **File formats:** Use `.dds` (DXT5 for alpha/transparency, DXT1 for opaque backgrounds) or 32-bit uncompressed `.tga`.
* **Naming convention:** Always prefix with `GFX_`.

---

## 3. Visual Layout Architecture (`interface/*.gui`)

### Coordinate System & Anchoring

Coordinates inside Clausewitz GUI files evaluate relative to their parent container anchor:

$$
\text{Final X} = \text{Anchor X} + \text{position.x}
$$

$$
\text{Final Y} = \text{Anchor Y} + \text{position.y}
$$

* **`orientation`**: Defines which point of the **parent container** acts as $(0,0)$.
  * Valid values: `UPPER_LEFT`, `UPPER_RIGHT`, `LOWER_LEFT`, `LOWER_RIGHT`, `CENTER`.
* **`origo`**: Defines which point of the **element itself** aligns to the anchor position.
  * Valid values: `upper_left`, `upper_right`, `lower_left`, `lower_right`, `center`.

### Standard Elements

#### 1. Container Window (`containerWindowType`)
Containers group UI components and establish nested coordinate scopes.

```pdx
containerWindowType = {
    name = "custom_window"
    position = { x = -250 y = -200 }
    size = { width = 500 height = 400 }
    orientation = CENTER
    origo = center
    moveable = yes
    clipping = no

    background = {
        name = "Background"
        quadTextureSprite = "GFX_custom_tiled_window"
    }
}
```

#### 2. Buttons (`buttonType`)

```pdx
buttonType = {
    name = "confirm_button"
    position = { x = 20 y = 320 }
    quadTextureSprite = "GFX_custom_button"
    buttonFont = "hoi_16mbs"
    buttonText = "CONFIRM_ACTION_LOC"
    pdx_tooltip = "CONFIRM_ACTION_TOOLTIP"
    clicksound = click_default
    shortcut = "RETURN"
}
```

#### 3. Text Boxes (`instantTextBoxType`)

```pdx
instantTextBoxType = {
    name = "header_title"
    position = { x = 20 y = 20 }
    font = "hoi_24header"
    text = "MY_HEADER_LOC_KEY"
    maxWidth = 460
    maxHeight = 30
    format = center        # Valid options: left, center, right
    fixedsize = yes
    truncate = yes
}
```

#### 4. Dynamic Lists (`gridBoxType`)
Renders elements populated dynamically via scripted GUI arrays.

```pdx
gridBoxType = {
    name = "custom_members_grid"
    position = { x = 10 y = 60 }
    size = { width = 100% height = 100% }
    slotsize = { width = 200 height = 40 }
    max_slots_horizontal = 1
    format = "UPPER_LEFT"
}
```

#### 5. Dropdown Menus (`dropDownBoxType` & `expandedWindow`)
Dropdowns consist of a collapsed trigger container and an animated unfolding popup window (`expandedWindow`).

```pdx
dropDownBoxType = {
    name = "custom_dropdown"
    position = { x = 150 y = 114 }
    size = { width = 250 height = 30 }
    expandedOnTop = yes  # CRITICAL: Ensures the popup renders above underlying buttons/canvas

    # 1. Collapsed State Display
    containerWindowType = {
        name = "dropdown_bg"
        size = { width = 250 height = 30 }
        background = {
            name = "name_bg"
            quadTextureSprite = "GFX_generic_background"
            alwaystransparent = yes
        }
    }

    instantTextboxType = {
        name = "name"
        position = { x = 25 y = 5 }
        font = "hoi_18mbs"
        maxWidth = 215
        maxHeight = 20
        fixedsize = yes
        format = left
    }

    expandButton = {
        name = "expand_button"
        position = { x = -9 y = 6 }
        quadTextureSprite = "GFX_expand_button"
        buttonFont = "Main_14_black"
        Orientation = "UPPER_RIGHT"
        clicksound = click_default
    }

    # 2. Expanded Popup Window
    expandedWindow = {
        name = "expanded_window"
        position = { x = 10 y = -160 }       # Offscreen start for animation
        show_position = { x = 10 y = 25 }     # Final target offset relative to dropdown anchor
        show_animation_type = decelerated
        hide_animation_type = accelerated
        animation_time = 300
        size = { width = 340 height = 440 }
        verticalScrollbar = "right_vertical_slider"
        scroll_wheel_factor = 60              # Exact multiple of slot height (e.g. 2 x 30px)
        smooth_scrolling = yes
        margin = { top = 7 bottom = 7 right = 6 }

        background = {
            name = "Background"
            quadTextureSprite = "GFX_tiled_window_1b_thin_border"
        }

        gridBoxType = {
            name = "items_grid"
            position = { x = 8 y = 0 }
            size = { width = 304 height = 100% }
            slotsize = { width = 304 height = 30 }  # Must match entry container width
            max_slots_horizontal = 1
            format = "UPPER_LEFT"
        }
    }
}
```

---

## 4. Scripted GUI Logic (`common/scripted_guis/*.txt`)

Scripted GUIs bridge the layout elements with game state, triggers, and execution effects.

```pdx
scripted_gui = {
    custom_window_logic = {
        context_type = player_context    # Options: player_context, country_context, selected_state_context
        window_name = "custom_window"    # Must match the containerWindowType name

        visible = {
            has_government = democratic
            NOT = { has_war = yes }
        }

        effects = {
            confirm_button_click = {
                # Executes when the button named 'confirm_button' is clicked
                custom_effect_tooltip = CONFIRM_BUTTON_EFFECT_DESC
                add_political_power = 50
                hidden_effect = {
                    set_country_flag = custom_gui_button_used
                }
            }
        }

        triggers = {
            confirm_button_click_enabled = {
                # Determines if 'confirm_button' is active or disabled/grayed out
                political_power > 49
            }
        }

        dynamic_lists = {
            custom_members_grid = {
                array = allies
                change_scope = yes
                entry_container = "custom_member_entry"
            }
        }

        ai_enabled = {
            always = no
        }
    }
}
```

---

## 5. In-Game Developer & Debug Tools

To test interfaces quickly, run the game with `-debug` in your launch options.

| Command / Shortcut | Description |
| :--- | :--- |
| `gui editor` | Toggles the visual GUI editor to drag, reposition, and inspect elements live. |
| `reload interface` | Hot-reloads `.gui` and `.gfx` files without restarting the client. |
| `reload scripted_guis` | Reloads triggers, scopes, and click effects from `common/scripted_guis/`. |
| `Ctrl + Alt + Click` | Inspects any hovered element and outputs its hierarchy path to the console. |
| `error.log` | Located in `Documents/Paradox Interactive/Hearts of Iron IV/logs/error.log`. |

---

## 6. Critical Modding Rules

1. **Strict Bracket Matching**: Every missing or extra brace (`}`) will silently fail parsing from that line downward, breaking subsequent UI assets.
2. **Coordinate Scoping**: Elements placed inside a `containerWindowType` calculate `x = 0, y = 0` from the container's top-left boundary, not the monitor display edge.
3. **Localization Encoding**: Clausewitz requires `UTF-8 with BOM` for all localization files (`.yml`). Standard UTF-8 without BOM results in corrupted text or missing tooltips.
4. **Namespace Uniqueness**: Always prefix your element names and sprites (e.g., `MYMOD_window_bg`) to prevent overriding vanilla game menus accidentally.
5. **Dropdown Layering (`expandedOnTop`)**: Always declare `expandedOnTop = yes` on `dropDownBoxType`. Without this, opening a dropdown over other UI containers (e.g. division template grids, equipment slot buttons) can cause click events to bleed through or underlying graphics to render over the dropdown.
6. **Usable Slot Width Math**: In any scrollable window with `verticalScrollbar = "right_vertical_slider"`, calculate usable entry width as:
   $$\text{Usable Width} = \text{Window Width} - \text{grid.x} - \text{margin.right} - \text{Scrollbar Width } (\approx 18\text{px}) - \text{padding } (\approx 2\text{--}4\text{px})$$
   Always set `slotsize.width` equal to the entry `containerWindowType.width`. Mismatched slot sizes cause hover highlight textures to misalign or clip into the scrollbar gutter.
7. **Integer Multiples for `scroll_wheel_factor`**: Set `scroll_wheel_factor` to an exact integer multiple of entry slot height ($N \times \text{slotsize.height}$). Fractional factors (such as vanilla's 45 for 30px slots) cause awkward half-row scrolling offsets.