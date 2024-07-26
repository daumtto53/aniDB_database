import re

class NovelInfo:

    def __init__(self):
        self.title = None
        self.description = None
        self.type = None
        self.year = None
        # [{title:"", relation:""}]
        self.related_series = {}
        # [{title:"", novel/manga:"", name_origin_country:""}, ...]
        self.associated_names = {}
        # {volumes:(int), complete/ongoing==true/false}
        self.status_in_origin_country = {}
        # [{season_starts_at:INT, volume_starts_at:INT, season_ends_at:INT, volume_ends_at:INT}, ...]
        self.artists = []
        self.original_publisher = []
        self.serialized_in = []
        self.genre=[]
        # [{start:"", end:""}, ]
        self.anime_start_and_end = []


    # Getter and Setter for title
    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, title):
        pattern = re.compile(r'([!@#$%^&*().\'"\w\d]+)[ \w]+')
        pattern.match(title)
        self._title = title

    # Getter and Setter for description
    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        self._description = value

    # Getter and Setter for type
    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, value):
        self._type = value

    # Getter and Setter for year
    @property
    def year(self):
        return self._year

    @year.setter
    def year(self, value):
        self._year = value

    # Getter and Setter for related_series
    @property
    def related_series(self):
        return self._related_series

    @related_series.setter
    def related_series(self, value):
        self._related_series = value

    # Getter and Setter for associated_names
    @property
    def associated_names(self):
        return self._associated_names

    @associated_names.setter
    def associated_names(self, value):
        self._associated_names = value

    # Getter and Setter for status_in_origin_country
    @property
    def status_in_origin_country(self):
        return self._status_in_origin_country

    @status_in_origin_country.setter
    def status_in_origin_country(self, value):
        self._status_in_origin_country = value

    # Getter and Setter for artists
    @property
    def artists(self):
        return self._artists

    @artists.setter
    def artists(self, value):
        self._artists = value

    # Getter and Setter for original_publisher
    @property
    def original_publisher(self):
        return self._original_publisher

    @original_publisher.setter
    def original_publisher(self, value):
        self._original_publisher = value

    # Getter and Setter for serialized_in
    @property
    def serialized_in(self):
        return self._serialized_in

    @serialized_in.setter
    def serialized_in(self, value):
        self._serialized_in = value

    # Getter and Setter for genre
    @property
    def genre(self):
        return self._genre

    @genre.setter
    def genre(self, value):
        self._genre = value

    # Getter and Setter for anime_start_and_end
    @property
    def anime_start_and_end(self):
        return self._anime_start_and_end

    @anime_start_and_end.setter
    def anime_start_and_end(self, value):
        self._anime_start_and_end = value

