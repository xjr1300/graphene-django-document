# Djangoデバッグミドルウェア

<https://docs.graphene-python.org/projects/django/en/latest/debug/>

- [Djangoデバッグミドルウェア](#djangoデバッグミドルウェア)
  - [インストール](#インストール)
  - [問い合わせ](#問い合わせ)

[django-debug-toolbar](https://django-debug-toolbar.readthedocs.org/)と似たような方法でGraphQLクエリをデバッグできますが、結果はグラフィカルなHTMLインターフェイスではなく、GraphQLレスポンスのフィールドとして出力されます。

そのため、grapheneのスキーマにプラグインを追加する必要があります。

## インストール

GrapheneのDjangoデバッグプラグインを使用するためには、次を行う必要があります。

- `GRAPHENE`設定内の`MIDDLEWARE`内に`graphene_django.debug.DjangoDebugMiddleware`を追加します。
- `graphene.Field(DjangoDebug, name="_debug")`値を持つ`debug`フィールドをスキーマルートの`Query`に追加します。

```python
from graphene_django.debug import DjangoDebug


class Query(graphene.ObjectType):
    debug = graphene.Field(DjangoDebug, name="_debug")


schema = graphene.Schema(query=Query)
```

そして、`settings.py`に次を設定します。

```python
GRAPHENE = {
    "MIDDLEWARE": [
        "graphene_django.debug.DjangoDebugMiddleware",
    ]
}
```

## 問い合わせ

次のようにクエリを実行して、GraphQL リクエストで発生したすべての SQL トランザクションを出力できます。

```graphql
{
  # DBと相互作用するORMを使用した例です。
  allIngredients {
    edges {
      node {
        id,
        name
      }
    }
  }
  # ここはSQLクエリを出力するdebugフィールドです。
  _debug {
    sql {
      rawSql
    }
  }
}
```

`_debug`フィールドはクエリの最後のフィールドでなければならないことに注意してください。
