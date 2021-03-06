import math


class LatLonConverter:
    def __init__(self, canvas, bot_lat, left_lon, top_lat, right_lon):
        self.canvas_width = canvas.width
        self.canvas_height = canvas.height
        self.top_lat = float(top_lat)
        self.left_lon = float(left_lon)
        self.bot_lat = float(bot_lat)
        self.right_lon = float(right_lon)

        # get global reference points to scale local x y appropriately
        self.tlx, self.tly = self.lat_lon_to_global_xy(self.top_lat, self.left_lon)
        self.brx, self.bry = self.lat_lon_to_global_xy(self.bot_lat, self.right_lon)
        self.x_range = self.brx - self.tlx
        self.y_range = self.bry - self.tly

    def lat_lon_to_global_xy(self, lat, lon):
        """converts latitude and longitude to global planar coordinates"""
        # equirectangular projection
        earth_radius = 6.371  # in km
        center_lat = (self.top_lat + self.bot_lat) / 2
        x = earth_radius * float(lon) * math.cos(math.radians(float(center_lat)))
        y = earth_radius * float(lat)
        return x, y

    def global_xy_to_local_xy(self, x, y):
        """converts global planar coordinates to local coordinates"""
        local_x = ((x - self.tlx)/self.x_range) * self.canvas_width
        local_y = ((y - self.tly)/self.y_range) * self.canvas_height
        return local_x, local_y

    def lat_lon_to_local_xy(self, lat, lon):
        global_x, global_y = self.lat_lon_to_global_xy(lat, lon)
        return self.global_xy_to_local_xy(global_x, global_y)
