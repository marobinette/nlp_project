"""
Any data related constants or functions should live in this file.
"""


class CCData:
    """
    Class for managing Course Catalog (CC) data constants and functionality.
    
    Provides access to university information, IPEDS ID mappings, and related utilities.
    """
    
    UNIVERSITY_DICTIONARY = {
        100663: "University of Alabama at Birmingham",
        100751: "The University of Alabama",
        102553: "University of Alaska Anchorage",
        110635: "University of California-Berkeley",
        110662: "University of California-Los Angeles",
        126614: "University of Colorado Boulder",
        129020: "University of Connecticut",
        134097: "Florida State University",
        142115: "Boise State University",
        147767: "Northwestern University",
        156125: "Wichita State University",
        163286: "University of Maryland-College Park",
        166638: "University of Massachusetts-Boston",
        187985: "University of New Mexico-Main Campus",
        190415: "Cornell University",
        199120: "University of North Carolina at Chapel Hill",
        199148: "University of North Carolina at Greensboro",
        200280: "University of North Dakota",
        231174: "University of Vermont",
    }
    
    @classmethod
    def get_dictionary(cls) -> dict[int, str]:
        """
        Get the full university dictionary.
        
        Returns:
            Dictionary mapping IPEDS IDs to university names
        """
        return cls.UNIVERSITY_DICTIONARY.copy()


# Backward compatibility: export the dictionary directly
UNIVERSITY_DICTIONARY = CCData.UNIVERSITY_DICTIONARY