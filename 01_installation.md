# インストール

Graphene-Djangoは、インストールと準備に数分かかります。

## 要求事項

現在、Graphene-Djangoは、Djangoの次に示すバージョンをサポートしています。

- >= Django 1.11

## インストール

```sh
pip install graphene-django
```

**Graphene-Djangoの新しいバージョンが、あなたのプロジェクトに破壊的な変更を導入する可能性があるため、Graphene-Djangoの特定のバージョンに固定することを強く推奨します。**

あなたのDjangoプロジェクトの`settings.py`ファイルにある`INSTALLED_APPS`に`graphene_django`を追加してください。

```python
# settings.py
INSTALLED_APPS = [
    ...
    "django.contrib.staticfiles", # GraphQLが要求するため
    "graphene_django"
]
```

あなたのDjangoプロジェクトの`urls.py`に`graphql`URLを追加する必要があります。

- Django 1.11の場合

  ```python
  from django.conf.urls import url
  from graphene_django.views import GraphQLView

  urlpatterns = [
      # ...
      url(r"graphql", GraphQLView.as_view(graphiql=True)),  # graph**i**qlであることに注意
  ]
  ```

- Django 2.0とそれ以上の場合

  ```python
  from django.urls import path
  from graphene_django.views import GraphQLView

  urlpatterns = [
      # ...
      path("graphql", GraphQLView.as_view(graphiql=True)),  # graph**i**qlであることに注意
  ]
  ```

  （もしあなたがGraphQL APIブラウザーを使用するつもりがないのであれば、`graphiql=True`を`graphiql=False`に変更してください。）

最後に、あなたのDjangoプロジェクトの`settings.py`ファイル内に、Grapheneが使用するスキーマの場所を定義します。

```python
GRAPHENE = {
  "SCHEMA": "django_root.schema.schema",
}
```

`path.schema.schema`の場所は、あなたのDjangoプロジェクトの`Schema`オブジェクトの場所です。
最も基本的な`schema.py`は次のようになります。

```python
import graphene


class Query(graphene.ObjectType):
    hello = graphene.String(default_value="Hi!")


schema = graphene.Schema(query=Query)
```

あなたのプロジェクトでスキーマオブジェクトを拡張する方法を学ぶために、基本的なチュートリアルを読んでください。

## CSRFの無効化

もし、あなたのDjangoプロジェクトで、あなたが[CSRF保護](https://docs.djangoproject.com/en/5.0/ref/csrf/)を有効にした場合、あなたはAPIクライアントが`graphql`エンドポイントへのPOSTリクエストが阻止されることに気付くでしょう。
あなたは、それぞれのリクエストでCSRFトークンを渡すようにAPIクライアントを更新することも、`csrf_exempt`デコレーターで`GraphQLView`をラップすることで、あなたのGraphQLエンドポイントをCSRF保護から除外することもできます。

[ajax - Djangoドキュメント](https://docs.djangoproject.com/en/5.0/ref/csrf/#ajax)

```python
# urls.py

from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from graphene_django.views import GraphQLView

urlpatterns = [
    # ...
    path("graphql", csrf_exempt(GraphQLView.as_view(graphiql=True))),
]
```
