"""
British National Grid - OS Grid Reference Converter
Copyright Edward Alan Lockhart, 2023

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see https://www.gnu.org/licenses/.
"""

def inverse_mapping(letters_dict):
    inv = {}
    for x, y_dict in letters_dict.items():
        for y, letter in y_dict.items():
            inv[letter] = (x, y)
    return inv

def xy_to_osgb(easting, northing, precision = 1):
    if precision not in [100000, 10000, 1000, 100, 10, 1]:
        raise Exception('Precision of ' + str(precision) + ' is not supported')

    try:
        x_idx = easting // 500000
        y_idx = northing // 500000
        major_letter = MAJOR_LETTERS[x_idx][y_idx]

        macro_easting = easting % 500000
        macro_northing = northing % 500000
        macro_x_idx = macro_easting // 100000
        macro_y_idx = macro_northing // 100000
        minor_letter = MINOR_LETTERS[macro_x_idx][macro_y_idx]
        
    except (ValueError, IndexError, KeyError, AssertionError):
        raise Exception('Out of range')

    micro_easting = macro_easting % 100000
    micro_northing = macro_northing % 100000

    ref_x = micro_easting // precision
    ref_y = micro_northing // precision

    gridref_width = 0
    if precision == 10000: gridref_width = 1
    elif precision == 1000: gridref_width = 2
    elif precision == 100: gridref_width = 3
    elif precision == 10: gridref_width = 4
    elif precision == 1: gridref_width = 5

    format_string = (r'%s%s %0' + str(gridref_width) + r'd %0' +
                     str(gridref_width) + r'd') if precision else r'%s%s %0'
    return format_string % (major_letter, minor_letter, ref_x, ref_y)

def osgb_to_xy(gridref, offset = False):
    try:
        tile, ref_x, ref_y = gridref.split()
        
        offset_dist = int('100000'[:-len(ref_x)])/2

        (x_maj, y_maj) = INV_MAJOR_LETTERS[tile[0]]
        (x_min, y_min) = INV_MINOR_LETTERS[tile[1]]

        assert len(ref_x) == len(ref_y) and len(ref_x) >= 1 and len(ref_x) <= 5
        gridref_width = len(ref_x)
        multiplier = 10**(5 - gridref_width)
        x_micro = int(ref_x)*multiplier
        y_micro = int(ref_y)*multiplier

    except (ValueError, IndexError, KeyError, AssertionError):
        raise Exception('Invalid format of coordinates')

    easting = x_maj*500000 + x_min*100000 + x_micro
    northing = y_maj*500000 + y_min*100000 + y_micro
    
    if offset: return (easting + offset_dist, northing + offset_dist)
    else: return (easting, northing)

MAJOR_LETTERS = {0: {0: 'S', 1: 'N', 2: 'H'},
                 1: {0: 'T', 1: 'O'}}
MINOR_LETTERS = {0: {0: 'V', 1: 'Q', 2: 'L', 3: 'F', 4: 'A'},
                 1: {0: 'W', 1: 'R', 2: 'M', 3: 'G', 4: 'B'},
                 2: {0: 'X', 1: 'S', 2: 'N', 3: 'H', 4: 'C'},
                 3: {0: 'Y', 1: 'T', 2: 'O', 3: 'J', 4: 'D'},
                 4: {0: 'Z', 1: 'U', 2: 'P', 3: 'K', 4: 'E'}}
INV_MAJOR_LETTERS = inverse_mapping(MAJOR_LETTERS)
INV_MINOR_LETTERS = inverse_mapping(MINOR_LETTERS)



def test():
    assert xy_to_osgb(432574, 332567, 10000) == 'SK 3 3'
    assert xy_to_osgb(236336, 682945, 10000) == 'NS 3 8'
    assert xy_to_osgb(392876, 494743, 10000) == 'SD 9 9'
    assert xy_to_osgb(472945, 103830, 10000) == 'SU 7 0'
    
    assert xy_to_osgb(432574, 332567, 1000) == 'SK 32 32'
    assert xy_to_osgb(236336, 682945, 1000) == 'NS 36 82'
    assert xy_to_osgb(392876, 494743, 1000) == 'SD 92 94'
    assert xy_to_osgb(472945, 103830, 1000) == 'SU 72 03'

    assert xy_to_osgb(432574, 332567, 100) == 'SK 325 325'
    assert xy_to_osgb(236336, 682945, 100) == 'NS 363 829'
    assert xy_to_osgb(392876, 494743, 100) == 'SD 928 947'
    assert xy_to_osgb(472945, 103830, 100) == 'SU 729 038'

    assert xy_to_osgb(432574, 332567, 10) == 'SK 3257 3256'
    assert xy_to_osgb(236336, 682945, 10) == 'NS 3633 8294'
    assert xy_to_osgb(392876, 494743, 10) == 'SD 9287 9474'
    assert xy_to_osgb(472945, 103830, 10) == 'SU 7294 0383'

    assert xy_to_osgb(432574, 332567, 1) == 'SK 32574 32567'
    assert xy_to_osgb(236336, 682945, 1) == 'NS 36336 82945'
    assert xy_to_osgb(392876, 494743, 1) == 'SD 92876 94743'
    assert xy_to_osgb(472945, 103830, 1) == 'SU 72945 03830'

    assert osgb_to_xy('SK 3     3') == (430000, 330000)
    assert osgb_to_xy('SK 32    32') == (432000, 332000)
    assert osgb_to_xy('SK 325   325') == (432500, 332500)
    assert osgb_to_xy('SK 3257  3256') == (432570, 332560)
    assert osgb_to_xy('SK 32574 32567') == (432574, 332567)
    
    assert osgb_to_xy('SP 5     0') == (450000, 200000)
    assert osgb_to_xy('SP 51    05') == (451000, 205000)
    assert osgb_to_xy('SP 517   052') == (451700, 205200)
    assert osgb_to_xy('SP 5175  0522') == (451750, 205220)
    assert osgb_to_xy('SP 51753 05225') == (451753, 205225)

    assert osgb_to_xy('SK 3     3', offset = True) == (435000, 335000)
    assert osgb_to_xy('SK 32    32', offset = True) == (432500, 332500)
    assert osgb_to_xy('SK 325   325', offset = True) == (432550, 332550)
    assert osgb_to_xy('SK 3257  3256', offset = True) == (432575, 332565)
    assert osgb_to_xy('SK 32574 32567', offset = True) == (432574.5, 332567.5)
    
    assert osgb_to_xy('SP 5     0', offset = True) == (455000, 205000)
    assert osgb_to_xy('SP 51    05', offset = True) == (451500, 205500)
    assert osgb_to_xy('SP 517   052', offset = True) == (451750, 205250)
    assert osgb_to_xy('SP 5175  0522', offset = True) == (451755, 205225)
    assert osgb_to_xy('SP 51753 05225', offset = True) == (451753.5, 205225.5)

test()
