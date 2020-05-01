"""
Morpheme definition file. 
If language gets complex, may be easier to manage as json.
"""


low_high_med = [
    {
        'frequency': {
            'value': None,
            'duration_range': None,
            'diff_from_previous': {
                'min_semitones': 4,
                'max_semitones': 6
            }
        },
        'time': {
            'since_previous': 2,
            'since_first': 2
        }
    },
    {
        'frequency': {
            'value': None,
            'duration_range': None,
            'diff_from_previous': {
                'min_semitones': -4,
                'max_semitones':-2 
            }
        },
        'time': {
            'since_previous': 2,
            'since_first': 10
        }
    }
]


do_re_mi = [
    {
        'frequency': {
            'value': None,
            'duration_range': None,
            'diff_from_previous': {
                'min_semitones': 1.5,
                'max_semitones': 2.5
            }
        },
        'time': {
            'since_previous': 2,
            'since_first': 2
        }
    },
    {
        'frequency': {
            'value': None,
            'duration_range': None,
            'diff_from_previous': {
                'min_semitones': 1.5,
                'max_semitones': 2.5
            }
        },
        'time': {
            'since_previous': 2,
            'since_first': 10
        }
    }
]
