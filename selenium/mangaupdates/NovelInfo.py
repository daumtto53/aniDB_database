class NovelInfo:

    def __init__(self):
        self.description = None
        self.type = None
        # {title:"", relation:""}
        self.related_series = { }
        # {title:"", novel/manga:"", name_origin_country:""}
        self.associated_names = {}
        # {volumes:(int), complete/ongoing==true/false}
        self.status_in_origin_country = True
        # [{season_starts_at:INT, volume_starts_at:INT, season_ends_at:INT, volume_ends_at:INT}, ...]
        self.anime_start_and_end = []
        self.genre=[]
        self.authors = []
        self.artists = []
        self.year = None
        self.original_publisher = None
        self.serialized_in = None


