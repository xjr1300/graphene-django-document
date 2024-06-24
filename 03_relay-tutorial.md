# Relayチュートリアル

<https://docs.graphene-python.org/projects/django/en/latest/tutorial-relay/>

- [Relayチュートリアル](#relayチュートリアル)
  - [Djangoプロジェクトの準備](#djangoプロジェクトの準備)
  - [モデルの定義](#モデルの定義)
  - [いくつかのテストデータの読み込み](#いくつかのテストデータの読み込み)
  - [スキーマ](#スキーマ)
  - [これまですべてをテストする](#これまですべてをテストする)
    - [設定の更新](#設定の更新)
    - [GraphQLとGraphiQLビューの作成](#graphqlとgraphiqlビューの作成)
    - [GraphQLスキーマをテストする](#graphqlスキーマをテストする)
  - [最後のステップ](#最後のステップ)

Grapheneは、*本当に簡単に*Djangoと機能させるために設計された追加的な機能を多く持っていまs樹。

注意事項: このクイックスタートのコードは、[cookbookのアプリ例](https://github.com/graphql-python/graphene-django/tree/master/examples/cookbook)から引用されました。

最初に次の文書を確認することは良い考えです。

- [Graphene Relayドキュメント](http://docs.graphene-python.org/en/latest/relay/)
- [GraphQL Relay仕様](https://facebook.github.io/relay/docs/en/graphql-server-specification.html)

## Djangoプロジェクトの準備

プロジェクトを準備して、次を作成してください。

- `cookbook`と呼ばれるDjangoプロジェクト
- `ingredients`と呼ばれるのアプリ

> 公式のチュートリアルは、`cookbook`ディレクトリ内に`ingredients`アプリを作成しているが、ここではプロジェクトディレクトリの直下に作成する。

```sh
# プロジェクトディレクトリを作成
mkdir cookbook
cd cookbook

# パッケージの依存関係をローカルに分離するために仮想環境を作成
python -m venv .venv
source .venv/bin/activate

# DjangoとDjangoをサポートしたGrapheneをインストール
pip install django
pip install graphene_django

# 1つのアプリケーションを持つ新しいプロジェクトを準備
django-admin startproject cookbook .  # 末尾の"."文字に注意
# cd cookbook
django-admin startapp ingredients
```

ここで、最初のデータベースを同期してください。

```sh
python manage.py migrate
```

いくつか単純なモデルを作成しましょう。

## モデルの定義

これらのモデルを使用して始めましょう。

```python
# ingredients/models.py
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=100)
    notes = models.TextField()
    category = models.ForeignKey(Category, related_name='ingredients')

    def __str__(self):
        return self.name
```

マイグレーションを作成して実行することを忘れないでください。

```sh
python manage.py makemigrations
python manage.py migrate
```

## いくつかのテストデータの読み込み

現在は、いくつかのテストデータを読み込む良いときです。
もっとも簡単な選択肢は、[ingredients.jsonフィクスチャーをダウンロード](https://raw.githubusercontent.com/graphql-python/graphene-django/master/examples/cookbook/cookbook/ingredients/fixtures/ingredients.json)して、`ingredients/fixtures/ingredients.json`に配置することです。
そして、次を実行できます。

```sh
python manage.py loaddata ingredients
```

代わりに、自分でいくつかのデータを作成するためにDjango管理インターフェイスを利用できます。
下を確認して、開発サーバーを起動して、`manage.py createsuperuser`で自分のログイン（アカウント）を作成する必要があります。

## スキーマ

GraphQLは、慣れ親しんだ階層的な構造ではなく、グラフ構造の世界でオブジェクトを与えます。
この表現を作成するために、Grapheneはグラフ内に現れるそれぞれのオブジェクトの*型*を知る必要があります。

また、このグラフは、すべてのアクセスが開始する*ルートタイプ*を持ちます。
これは、下の`Query`クラスです。
この例において、`all_ingredients`を使用してすべての材料をリストする能力と、`ingredient`を使用して特定の材料を獲得する能力を提供します。

`ingredients/schema.py`ファイルを作成して、次をタイプしてください。

```python
# ingredients/schema.py
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
```

フィルタリング機能は、[django-filter](https://django-filter.readthedocs.org/)によって提供されています。
`filter_fields`の書式の詳細は、[使用方法ドキュメント](https://django-filter.readthedocs.org/en/latest/guide/usage.html#the-filter)を参照してください。
オプションではありますが、このチュートリアルではこの機能を使用するため、このチュートリアルを機能させるために、`django-filter`をインストールする必要があります。

```sh
pip install django-filter
```

上記の`Query`クラスは`abstract`としてマークされていることに注意してください。
これは、すべてのアプリケーションレベルのクエリを結合した、プロジェクトレベルのクエリを現在作成することが理由です。

親のプロジェクトレベルの`schema.py`を作成します。

```python
import graphene

import ingredients.schema


class Query(ingredients.schema.Query, graphene.ObjectType):
    # プロジェクトにさらにアプリを追加した場合、このクラスは複数のクエリから派生されるようになります。
    pass


schema = graphene.Schema(query=Query)
```

現在、名前空間が欠けてていますが、これを最上位の`urls.py`ファイルのように捉えることができます。

## これまですべてをテストする

### 設定の更新

次に、Djangoプロジェクトに、アプリとGraphiQLをインストールします。
GraphiQLは、GraphQLクエリを記述して実行することを支援するための、Webベースの統合開発環境です。
それは、cookbookプロジェクトを単純かつ容易な方法でテストできるようにします。

`cookbook/settings.py`内の`INSTALLED_APPS`に`ingredients`と`graphene_django`を追加してください。

```python
INSTALLED_APPS = [
    ...
    # また、これは`graphql_schema`管理コマンドを利用できるようにします。
    'graphene_django',

    # ingredientsアプリをインストールします。
    'ingredients',
]
```

そして、`cookbook/settings.py`の`GRAPHENE`設定に`SCHEMA`を追加してください。

```python
GRAPHENE = {
    'SCHEMA': 'cookbook.schema.schema'
}
```

代わりに、下で説明したように、（スキーマを）使用できるようにURL定義内でスキーマを指定できます。

### GraphQLとGraphiQLビューの作成

RESTful APIと異なり、GraphQLはアクセスされるたった1つのURL歯科ありません。
このURLへのリクエストは、Grapheneの`GraphQLView`ビューによって処理されます。

このビューは、GraphQLエンドポイントとしての役目を果たします。
前述のGraphiQLが必要なため、`graphiql=True`パラメーターを指定してください。

```python
from django.conf.urls import url, include
from django.contrib import admin

from graphene_django.views import GraphQLView

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^graphql$', GraphQLView.as_view(graphiql=True)),
]
```

もし、上記で説明したDjango設定ファイル内に目的となるスキーマを指定していない場合、ここに示したことをすることで指定できます。

```python
from django.conf.urls import url, include
from django.contrib import admin

from graphene_django.views import GraphQLView

from schema import schema

urlpatterns = [
    url('admin/', admin.site.urls),
    url('graphql', csrf_exempt(GraphQLView.as_view(graphiql=True, schema=schema))),
]
```

### GraphQLスキーマをテストする

これで、構築したAPIをテストする準備ができました。
コマンドラインからサーバーを起動しましょう。

```sh
python manage.py runserver
```

[localhost:8000/graphql](http://localhost:8000/graphql)にアクセスして、最初のクエリをタイプしてください。

```graphql
query {
  allIngredients {
    edges {
      node {
        id
        name
      }
    }
  }
}
```

上記は、すべての材料の名前とIDを返します。
ところで、しかし、特定の材料を欲しいと場合は次のように問い合わせします。

```graphql
query {
  # Grapheneはすべてのオブジェクトのグローバルに一意なIDを生成します。
  # 最初のクエリの結果からこの値をコピーする必要があるかもしれません。
  ingredient(id: "SW5ncmVkaWVudE5vZGU6MQ==") {
    name
  }
}
```

また、それぞれのカテゴリのそれぞれの材料を得ることもできます。

```graphql
query {
  allCategories {
    edges {
      node {
        name
        ingredients {
          edges {
            node {
              name
            }
          }
        }
      }
    }
  }
}
```

または、文字`'e'`を含む肉の材料のみを得ることができます。

```graphql
query {
  allIngredients(name_Icontains: "e", category_Name: "Meat") {
    edges {
      node {
        name
      }
    }
  }
}
```

## 最後のステップ

Relayと一緒に機能するGraphQLのエンドポイントを作成しましたが、Relayが機能するために、それはスキーマにアクセスする必要があります。
スキーマをエクスポートする命令は、このガイドの[イントロスペクションスキーマ](http://docs.graphene-python.org/projects/django/en/latest/introspection/)パートで見つけることができます。
