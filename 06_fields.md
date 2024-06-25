# フィールド

<https://docs.graphene-python.org/projects/django/en/latest/fields/>

- [フィールド](#フィールド)
  - [DjangoListField](#djangolistfield)
  - [カスタムリゾルバー](#カスタムリゾルバー)
  - [DjangoConnectionField](#djangoconnectionfield)

Graphene-Djangoは、DjangoをGraphQLスキーマと統合することを助けるいくつかの便利なフィールドを提供しています。

## DjangoListField

`DjangoListField`は、[DjangoObjectType](https://docs.graphene-python.org/projects/django/en/latest/queries/#queries-objecttypes)のリストを定義できるようにします。
デフォルトで、`DjangoListField`は、Djangoモデルのデフォルトのクエリセットに解決します。

```python
from graphene import ObjectType, Schema
from graphene_django import DjangoListField


class RecipeType(DjangoObjectType):
    class Meta:
        model = Recipe
        fields = ("title", "instructions")


class Query(ObjectType):
    recipes = DjangoListField(RecipeType)


schema = Schema(query=Query)
```

上記コードは、次のスキーマ定義を生じます。

```graphql
schema {
  query: Query
}

type Query {
  recipes: [RecipeType]
}

type RecipeType {
  title: String!
  instructions: String!
}
```

## カスタムリゾルバー

`DjangoObjectType`が、カスタムな[get_queryset](https://docs.graphene-python.org/projects/django/en/latest/queries/#django-objecttype-get-queryset)メソッドを定義している場合、`DjangoListField`を解決するとき、それは、もし定義されている場合はフィールドリゾルバーの戻り値を、そうでない場合はDjangoモデルのデフォルトのクエリセットを呼び出します。

> フィールドリゾルバーが定義されている場合、それが優先される。

例えば、次のスキーマは、公開されていて、タイトルを持つレシピのみを解決します。

```python
from graphene import ObjectType, Schema
from graphene_django import DjangoListField


class RecipeType(DjangoObjectType):
    class Meta:
        model = Recipe
        fields = ("title", "instructions")

    @classmethod
    def get_queryset(cls, queryset, info):
        # タイトルを持っていないレシピをフィルタアウトします。
        return queryset.exclude(title__exact="")


class Query(ObjectType):
    recipes = DjangoListField(RecipeType)

    def resolve_recipes(parent, info):
        # 公開されているレシピのみを取得します。
        return Recipe.objects.filter(published=True)


schema = Schema(query=Query)
```

> `recipes`フィールドが問い合わされたとき、`RecipeType.get_queryset`メソッドの結果が`Query.resolve_recipes`メソッドで使用される。

## DjangoConnectionField

ドキュメントなし。
