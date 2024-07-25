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
        self.authors = []
        self.artists = []
        self.original_publisher = []
        self.serialized_in = []
        self.genre=[]
        self.anime_start_and_end = []

