# 基本的なチュートリアル

<https://docs.graphene-python.org/projects/django/en/latest/tutorial-plain/#>

- [基本的なチュートリアル](#基本的なチュートリアル)
  - [Djangoプロジェクトの準備](#djangoプロジェクトの準備)
  - [モデルの定義](#モデルの定義)
  - [いくつかのテストデータのロード](#いくつかのテストデータのロード)
  - [こんにちはGraphQL - スキーマとオブジェクトタイプ](#こんにちはgraphql---スキーマとオブジェクトタイプ)
  - [これまでのすべてをテスト](#これまでのすべてをテスト)
    - [設定の更新](#設定の更新)
    - [GraphQLとGraphiQLビューの作成](#graphqlとgraphiqlビューの作成)
    - [GraphQLスキーマのテスト](#graphqlスキーマのテスト)
    - [関連を得る](#関連を得る)
  - [まとめ](#まとめ)

Graphene-Djangoは、容易にDjangoと機能するために設計された、いくつかの追加的な機能があります。
このチュートリアルで重点的に取り組むことは、DjangoのORMからGrapheneオブジェクトタイプへ接続する方法の良い理解を与えることです。

## Djangoプロジェクトの準備

プロジェクトを準備して、次を作成します。

- `cookbook`と呼ばれるDjangoプロジェクト
- `ingredients`と呼ばれる`cookbook`内のアプリ

```sh
# プロジェクトディレクトリを作成
mkdir cookbook
cd cookbook

# ローカルに依存パッケージを隔離するために仮想環境を作成
python -m venv .venv
source .venv/bin/activate

# DjangoとDjangoをサポートしたGrapheneをインストール
pip install django graphene_django

# 1つのアプリを持つ新しいプロジェクトをカレントディレクトリに作成
django-admin startproject cookbook .  # 末尾の"."文字に注意
# cd cookbook
# チュートリアルでは、cookbookディレクトリ内にアプリを作成しているが、
# プロジェクトディレクトリの下にアプリを作成
django-admin startapp ingredients
```

ここで、はじめてデータベースを同期します。

```python
python manage.py migrate
```

数個の単純なモデルを作成しましょう。

## モデルの定義

これらのモデルで開始しましょう。

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
    category = models.ForeignKey(
        Category, related_name="ingredients", on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name
```

`INSTALL_APPS`として`ingredients`を追加します。

```python
# cookbook/settings.py
INSTALLED_APPS = [
    ...
    # ingredientsアプリをインストール
    "ingredients",
]
```

マイグレーションの作成と実行を忘れないでください。

```sh
python manage.py makemigrations
python manage.py migrate
```

## いくつかのテストデータのロード

現在、いくつかのテストデータをロードする良い時です。
最も簡単な選択肢は、[ingredients.jsonフィクスチャ](https://raw.githubusercontent.com/graphql-python/graphene-django/master/examples/cookbook/cookbook/ingredients/fixtures/ingredients.json)をダウンロードして、`ingredients/fixtures/ingredients.json`に配置します。
その後、次を実行できます。

```sh
% python manage.py loaddata ingredients
Installed 6 object(s) from 1 fixture(s)
```

代わりに、あなたは、あなた自身でいくつかのデータを作成するためにDjangoの管理インターフェイスを使用できます。
あなたは、開発サーバーを実行して、管理パネルでモデルを登録するために、あなた自身のアカウントを作成する必要があります。

- 開発サーバーの実行: `python manage.py runserver`
- スーパーユーザーの作成: `python manage.py createsuperuser`

管理パネルにモデルを登録してください。

```python
from django.contrib import admin

from ingredients.models import Category, Ingredient

admin.site.register(Category)
admin.site.register(Ingredient)
```

## こんにちはGraphQL - スキーマとオブジェクトタイプ

Djangoプロジェクトでクエリを作成するために、いくつか必要なことをします。

- オブジェクトタイプで定義されてスキーマ
- 入力としてクエリを受け取り結果を返すビュー

GraphQLは、慣れ親しんだ階層構造ではなくグラフ構造で世界にあなたのオブジェクトを提示します。
この表現を作成するために、Grapheneは、グラフ内に現れるそれぞれのオブジェクトのタイプを理解する必要があります。

また、このグラフはすべてのアクセスが開始される*ルートタイプ*もあります。
これは下の`Query`クラスです。

DjangoモデルのそれぞれのGraphQLタイプを作成するために、Djangoモデルのフィールドに対応するGraphQLフィールドを自動的に定義する`DjangoObjectType`をサブクラス化します。

それを実施した後で、`Query`クラス内にフィールドとしてそれらをリストします。

`cookbook/schema.py`を作成して、次をタイプしてください。

```python
import graphene
from graphene_django import DjangoObjectType

from ingredients.models import Category, Ingredient


class CategoryType(DjangoObjectType):
    class Meta:
        model = Category
        fields = ("id", "name", "ingredients")


class IngredientType(DjangoObjectType):
    class Meta:
        model = Ingredient
        fields = ("id", "name", "notes", "category")


class Query(graphene.ObjectType):
    all_ingredients = graphene.List(IngredientType)
    category_by_name = graphene.Field(CategoryType, name=graphene.String(required=True))

    # def resolve_all_ingredients(root, info):
    def resolve_all_ingredients(self, info):
        return Ingredient.objects.select_related("category").all()

    # def resolve_category_by_name(root, info, name):
    def resolve_category_by_name(self, info, name):
        try:
            return Category.objects.get(name=name)
        except Category.DoesNotExist:
            return None


schema = graphene.Schema(query=Query)
```

あなたの最上位の`urls.py`ファイルのようにこれを捉える事ができます。

## これまでのすべてをテスト

次に移る前に、スキーマを更新して、Djangoが機能するかクエリをテストできるようにします。

### 設定の更新

次に、あなたのDjangoプロジェクトにあなたのアプリとGraphQLをインストールします。
GraphiQLは、GraphQLクエリを記述して実行する支援をしてくれるWebベースの統合開発環境です。
GraphiQLは、cookbookプロジェクトをテストする単純で簡単な方法を提供します。

`cookbook/settings.py`内の`INSTALLED_APPS`に`graphene_django`を追加します。

```python
# cookbook/settings.py
INSTALLED_APPS = [
    ...
    "django.contrib.staticfiles",
    "graphene_django",
    ...
]
```

そしてその後、`cookbook/settings.py`内の`GRAPHENE`に`SCHEMA`を追加します。

```python
# cookbook/settings.py
GRAPHENE = {
    "SCHEMA": "schema.schema",
}
```

> `"schema.schema"`は、プロジェクトディレクトリの`schema`モジュール(`schema.py`ファイル)内の`schema`オブジェクトを指している。

代わりに、後で説明するように、URL定義で使用するスキーマを指定することもできます。

### GraphQLとGraphiQLビューの作成

RESTful APIと異なり、GraphQLはアクセスされる1つのURLしかありません。
このURLへのリクエストはGrapheneの`GraphQLView`ビューによって処理されます。

このビューはGraphQLのエンドポイントとして提供されます。
前述のGraphiQLを使用したい場合は、パラメーターで`graphiql=True`を指定します。

```python
# cookbook/urls.py
from django.contrib import admin
from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from graphene_django.views import GraphQLView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("graphql", csrf_exempt(GraphQLView.as_view(graphiql=True))),
]
```

もし、上記で説明したDjango設定ファイル内に目的のスキーマを指定していない場合は、このようにできます。

```python
# cookbook/urls.py
from django.contrib import admin
from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from graphene_django.views import GraphQLView

from schema import schema

urlpatterns = [
    path("admin/", admin.site.urls),
    path("graphql", csrf_exempt(GraphQLView.as_view(graphiql=True, schema=schema))),
]
```

### GraphQLスキーマのテスト

現在、構築したAPIをエストする準備ができました。
コマンドラインからサーバーを起動しましょう。

```sh
% python manage.py runserver
Watching for file changes with StatReloader
Performing system checks...

System check identified no issues (0 silenced).
June 07, 2024 - 09:57:20
Django version 5.0.6, using settings 'cookbook.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

<localhost:8000/graphql>にアクセスして最初のクエリをタイプしてください。

```graphql
query {
  allIngredients {
    id
    name
  }
}
```

もじ、提供したフィクスチャーを使用している場合、次のレスポンスを確認するでしょう。

```json
{
  "data": {
    "allIngredients": [
      {
        "id": "1",
        "name": "Eggs"
      },
      {
        "id": "2",
        "name": "Milk"
      },
      {
        "id": "3",
        "name": "Beef"
      },
      {
        "id": "4",
        "name": "Chicken"
      }
    ]
  }
}
```

おめでとうございます。
機能するGraphQLサーバーを作成しました。

注意事項: Grapheneは、JavaScriptのクライアントと良い互換性を持つように、すべてのフィールドの名前を[自動でキャメルケース](http://docs.graphene-python.org/en/latest/types/schema/#auto-camelcase-field-names)にします。

### 関連を得る

現在のスキーマを使用することで、関連も問い合わせできます。
これが、GraphQLを本当に強力にします。

例えば、特定のカテゴリを得て、そのカテゴリに含まれるすべての材料(ingredients)をリストしたいかもしれません。

次のクエリでそれができます。

```graphql
query {
  categoryByName(name: "Dairy") {
    id
    name
    ingredients {
      id
      name
    }
  }
}
```

これは、フィクスチャーを使用している場合、次の結果を与えます。

```json
{
  "data": {
    "categoryByName": {
      "id": "1",
      "name": "Dairy",
      "ingredients": [
        {
          "id": "1",
          "name": "Eggs"
        },
        {
          "id": "2",
          "name": "Milk"
        }
      ]
    }
  }
}
```

また、すべての材料をリストして、それらが含まれるカテゴリの情報を得ることもできます。

```graphql
query {
  allIngredients {
    id
    name
    category {
      id
      name
    }
  }
}
```

```json
{
  "data": {
    "allIngredients": [
      {
        "id": "1",
        "name": "Eggs",
        "category": {
          "id": "1",
          "name": "Dairy"
        }
      },
      {
        "id": "2",
        "name": "Milk",
        "category": {
          "id": "1",
          "name": "Dairy"
        }
      },
      {
        "id": "3",
        "name": "Beef",
        "category": {
          "id": "2",
          "name": "Meat"
        }
      },
      {
        "id": "4",
        "name": "Chicken",
        "category": {
          "id": "2",
          "name": "Meat"
        }
      }
    ]
  }
}
```

## まとめ

これまで確認した通り、GraphQLはとても強力で、Djangoのモデルとの統合は、機能するサーバーを素早く開始できるようにします。

もし、`django-filter`や自動ページネーションのようなものを実際に実行したい場合は、[Relayチュートリアル](https://docs.graphene-python.org/projects/django/en/latest/tutorial-relay/#relay-tutorial)に進むべきです。

十分にGrapheneに慣れるために、[Grapheneのドキュメント](http://docs.graphene-python.org/en/latest/)を確認することは良い考えです。
