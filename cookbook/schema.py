import graphene
import ingredients.schema

# from graphene_django import DjangoObjectType
# from ingredients.models import Category, Ingredient
#
#
# class CategoryType(DjangoObjectType):
#     class Meta:
#         model = Category
#         fields = ("id", "name", "ingredients")
#
#
# class IngredientType(DjangoObjectType):
#     class Meta:
#         model = Ingredient
#         fields = ("id", "name", "notes", "category")
#
#
# class Query(graphene.ObjectType):
#     all_ingredients = graphene.List(IngredientType)
#     category_by_name = graphene.Field(CategoryType, name=graphene.String(required=True))
#
#     # def resolve_all_ingredients(root, info):
#     def resolve_all_ingredients(self, info):
#         return Ingredient.objects.select_related("category").all()
#
#     # def resolve_category_by_name(root, info, name):
#     def resolve_category_by_name(self, info, name):
#         try:
#             return Category.objects.get(name=name)
#         except Category.DoesNotExist:
#             return None


class Query(ingredients.schema.Query, graphene.ObjectType):
    # プロジェクトにさらにアプリを追加した場合、このクラスは複数のクエリから派生されるようになります。
    pass


schema = graphene.Schema(query=Query)
