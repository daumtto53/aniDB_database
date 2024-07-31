import logging
import re

class NovelInfo:

    def __init__(self):
        self.title = ''
        self.description = None
        self.type = None
        self.year = None
        # [{title:"", type(?,(Novel), relation:""}]
        self.related_series = []
        # [{title:"", novel/manga:"", name_origin_country:""}, ...]
        self.associated_names = []
        # {volumes:(int), complete/ongoing==true/false}
        self.status_in_origin_country = {}
        self.image_url = None
        # [{season_starts_at:INT, volume_starts_at:INT, season_ends_at:INT, volume_ends_at:INT}, ...]
        self.artists = []
        self.authors = []
        self.original_publisher = []
        self.serialized_in = []
        self.genres=[]
        # [{start:"", end:""}, ]
        self.anime_start_and_end = []

    def set_title(self, input_title):
        pattern = re.compile(r'^(.*?)(?:\s*\(.*\))?$')
        matched = pattern.match(input_title)
        if matched:
            self.title = matched.group(1)
        else:
            logging.info("NO TITLE: ")
            self.title = 'N/A'

    def set_description(self, value):
        pattern = re.compile(r'\s*Less\.\.\.$')
        value = re.sub(pattern, '', value)
        if value != 'N/A':
            self.description = value
        else:
            self.description = 'N/A'

    # Getter and Setter for type
    def set_type(self, value):
        if value != "N/A":
            self.type= value
        else:
            self.type= 'N/A'

    # Getter and Setter for related_series
    def set_related_series(self, value):
        if len(value) == 0 or value[0]['title'] == 'N/A':
            value = []
        else:
            self.related_series = value

    # Getter and Setter for associated_names
    def set_associated_names(self, value):
        if len(value) == 0 or value[0]['title'] == '':
            value = []
        else:
            self.associated_names = value

    # Getter and Setter for status_in_origin_country
    def set_status_in_origin_country(self, value):
        self.status_in_origin_country = value

    # Getter and Setter for anime_start_and_end
    def set_anime_start_and_end(self, value):
        self.anime_start_and_end = value

    def set_image_url(self, value):
        self.image_url= value

    # Getter and Setter for genre
    def set_genres(self, value):
        self.genres = value

    def set_authors(self, value):
        self.authors= value

    # Getter and Setter for artists
    def set_artists(self, value):
        self.artists = value

    def set_year(self, value):
        self.year = value

    # Getter and Setter for original_publisher
    def set_original_publisher(self, value):
        self.original_publisher = value

    # Getter and Setter for serialized_in
    def set_serialized_in(self, value):
        self.serialized_in = value

    def __str__(self):
        return (f'\n'
                f'title = {self.title}\n'
                f'description = {self.description}\n'
                f'type = {self.type}\n'
                f'year = {self.year}\n'
                f'related_series = {self.related_series}\n'
                f'associated_names = {self.associated_names}\n'
                f'status_in_origin_country = {self.status_in_origin_country}\n'
                f'image_url = {self.image_url}\n'
                f'artists = {self.artists}\n'
                f'authors = {self.authors}\n'
                f'original_publisher = {self.original_publisher}\n'
                f'serialized_in = {self.serialized_in}\n'
                f'genres = {self.genres}\n'
                f'anime_start_and_end = {self.anime_start_and_end}\n')
