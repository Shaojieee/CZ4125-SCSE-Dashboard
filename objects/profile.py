import json
import os



def save_list_of_profiles(profiles, output_dir='./data', output_filename='individual_profiles'):
    output = [x.to_dict() for x in profiles]
    
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, output_filename+'.csv')
    with open(output_file, 'w') as f:
        json.dump(output, f)
    print(f'Individual Profiles saved at {output_file}')
    return 


class Profile:
    def __init__(self, **kwargs):
        self.full_name = kwargs.get('full_name', None)
        self.name_card = kwargs.get('name_card', None)
        self.email = kwargs.get('email', None)
        self.designation = kwargs.get('designation', None)


        self.google_scholar = kwargs.get('google_scholar', None)
        self.orcid = kwargs.get('orcid', None)
        self.github = kwargs.get('github', None)
        self.scopus = kwargs.get('scopus', None)
        self.web_of_science = kwargs.get('web_of_science', None)
        self.dr_ntu = kwargs.get('dr_ntu', None)
        self.other_websites = kwargs.get('other_websites', None) 

        self.biography = kwargs.get('biography', None)
        self.keywords = kwargs.get('keywords', None)
        self.interests = kwargs.get('interest', None)
        self.grants = kwargs.get('grants', None)

        self.articles = kwargs.get('articles', None) 
        self.books = kwargs.get('books', None)
        self.book_chapters = kwargs.get('book_chapters', None)
        self.conferences = kwargs.get('conferences', None) 
        self.courses_taught = kwargs.get('courses_taught', None)

    def to_dict(self):
        return {key: value for key, value in self.__dict__.items() if not key.startswith('__')}
    