from graphene import ObjectType, relay
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from ingredients.models import Category, Ingredient


# Grapheneは、自動的にCategoryモデルフィールドをCategoryNodeにマッピングします。
# これは、下で確認できるように、CategoryNodeメタクラス内で構成されています。
class CategoryNode(DjangoObjectType):
    class Meta:
        model = Category
        filter_fields = ["name", "ingredients"]
        interfaces = (relay.Node,)


class IngredientNode(DjangoObjectType):
    class Meta:
        model = Ingredient
        # ここで、いくつかより応用的なフィルタをできるようにします。
        filter_fields = {
            "name": ["exact", "icontains", "istartswith"],
            "notes": ["exact", "icontains"],
            "category": ["exact"],
            "category__name": ["exact"],
        }
        interfaces = (relay.Node,)


class Query(ObjectType):
    category = relay.Node.Field(CategoryNode)
    all_categories = DjangoFilterConnectionField(CategoryNode)

    ingredient = relay.Node.Field(IngredientNode)
    all_ingredients = DjangoFilterConnectionField(IngredientNode)
