

class Profile():
    def __init__(self):
        self.full_name = None
        self.name_card = None
        self.email = None
        self.designation = None

        self.google_scholar = None
        self.orcid = None
        self.dr_ntu = None 

        self.biography = None
        self.keywords = None
        self.articles = None 
        self.conference = None 
        self.courses_taught = None

    def get_profile_dict(self):
        return  {key: value for key, value in self.__dict__.items() if not key.startswith('__')}
    
    