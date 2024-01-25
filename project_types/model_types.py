class Recipe:
    id: int
    name: str
    description: str
    num_of_servings: int
    cook_time: int
    directions: str
    is_publish: bool

    @property
    def data(self):
        return{
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'num_of_servings': self.num_of_servings,
            'cook_time': self.cook_time,
            'directions': self.directions
        }