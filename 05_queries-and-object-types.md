# クエリとオブジェクトタイプ

<https://docs.graphene-python.org/projects/django/en/latest/queries/>

- [クエリとオブジェクトタイプ](#クエリとオブジェクトタイプ)
  - [イントロダクション](#イントロダクション)
  - [完全な例](#完全な例)
  - [どのフィールドを含めるか指定する](#どのフィールドを含めるか指定する)
    - [fields](#fields)
    - [exclude](#exclude)
  - [フィールドのカスタマイズ](#フィールドのカスタマイズ)
  - [DjangoのchoicesとEnumの変換](#djangoのchoicesとenumの変換)
  - [関連したモデル](#関連したモデル)
  - [デフォルトクエリセット](#デフォルトクエリセット)
  - [リゾルバー](#リゾルバー)
    - [引数](#引数)
    - [Info](#info)
      - [DjangoObjectType](#djangoobjecttype)
  - [単純なObjectType](#単純なobjecttype)
  - [完全な例](#完全な例-1)

## イントロダクション

Graphene-Djangoは、GraphQLクエリを実行するために多くの機能を提供します。

Graphene-Djangoは、自動的にDjangoモデルを`ObjectType`に変換する特別な`DjangoObjectType`を提供します。

## 完全な例

```python
# my_app/schema.py
import graphene
from graphene_django import DjangoObjectType

from .models import Question


class QuestionType(DjangoObjectType):
    class Meta
        model = Question
        fields = ("id", "question_text")


class Query(graphene.ObjectType):
    questions = graphene.List(QuestionType)
    question_by_id = graphene.Field(QuestionType, id=graphene.String())

    def resolve_questions(root, info, **kwargs):
        # リストを問い合わせ
        return Question.objects.all()

    def resolve_question_by_id(root, info, id):
        # 1つの質問を問い合わせ
        return Question.objects.get(pk=id)
```

## どのフィールドを含めるか指定する

デフォルトで、`DjangoObjectType`は、GraphQLを経由してモデルのすべてのフィールドを与えます。
与えるフィールドを部分集合だけにしたい場合、`fields`または`exclude`を使用してそれができます。
フィールドの属性を使用して、公開すべきすべてのフィールドを明示的に設定することを、強く推奨します。
これは、モデルが変更されたときに、意図せずに公開されるデータが発生することがなくなるようになります。

### fields

モデルのこれらのフィールドだけを表示します。

```python
from graphene_django import DjangoObjectType

from .models import Question


class Question(DjangoObjectType):
    class Meta:
        model = Question
        fields = ("id", "question_text")
```

モデル内の使用されるべきすべてのフィールドを示す特別な値である`"__all__"`を`fields`属性に設定することもできます。

例えば・・・

```python
from graphene_django import DjangoObjectType

from .models import Question

class QuestionType(DjangoObjectType):
    class Meta:
        model = Question
        fields = "__all__"
```

### exclude

`exclude`内のそれらを除くすべてのフィールドを表示します。

```python
from graphene_django import DjangoObjectType

from .models import Question


class Question(DjangoObjectType):
    class Meta:
        model = Question
        exclude = ("question_text",)
```

## フィールドのカスタマイズ

リゾルバーを使用して、`DjangoObjectType`のフィールドを完全にオーバーライドでき、また新しいフィールドを追加できます。

```python
from graphene_django import DjangoObjectType

from .models import Question


class QuestionType(DjangoObjectType):
    class Meta:
        model = Question
        fields = ("id", "question_text")

    # 新しいフィールドを追加
    extra_field = graphene.String()

    def resolve_extra_field(self, info):
        """リゾルバーを使用して、新しいフィールドを公開"""
        return "Hello!"
```

## DjangoのchoicesとEnumの変換

デフォルトで、Graphene-Djangoは、[choices](https://docs.djangoproject.com/en/5.0/ref/models/fields/#choices)を定義した任意のDjangoフィールドから、GraphQLのEnum型に変換します。

例えば、次の`Model`と`DjangoObjectType`があるとします。

```python
from django.db import models
from graphene_django import DjangoObjectType


class PetModel(models.Model):
    kind = models.CharField(
        max_length=100,
        choices=(
            ("cat", "Cat"),
            ("dog", "Dog"),
        )
    )


class PetType(DjangoObjectType):
    class Meta:
        model = PetModel
        fields = ("id", "kind")
```

次のGraphQLスキーマ定義になります。

```graphql
type Pet {
  id: ID!
  kind: PetModelKind!
}

enum PetModelKind {
  CAT
  DOG
}
```

`DjangoObjectType`の`Meta`クラスの`convert_choices_to_enum`属性に`False`を設定することによって、この自動変換を無効にできます。

```python
from graphene_django import DjangoObjectType
from .models import PetModel


class Pet(DjangoObjectType):
    class Meta:
        model = PetModel
        fields = ("id", "kind")
        convert_choices_to_enum = False
```

```graphql
type Pet {
  id: ID!
  kind: String!
}
```

また、自動でEnumに変換したいフィールドのリストに`convert_choices_to_enum`を設定することもできます。

```python
from graphene_django import DjangoObjectType
from .models import PetModel


class Pet(DjangoObjectType):
    class Meta:
        model = PetModel
        fields = ("id", "kind")
        convert_choices_to_enum = ["kind"]
```

**注意事項:** `convert_choices_to_enum = []`を設定することは、それに`False`を設定したことと同じです。

## 関連したモデル

次のモデルがあるとします。

```python
from django.db import models


class Category(models.Model):
    foo = models.CharField(max_length=256)


class Question(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
```

`DjangoObjectType`として`Question`が公開され、次のように問い合わせ可能なフィールドとして`Category`を追加したいとします。

```python
from graphene_django import DjangoObjectType
from .models import Question


class QuestionType(DjangoObjectType):
    class Meta:
        models = Question
        fields = ("category",)
```

すると、すべてのクエリ可能な関連したモデルは、`DjangoObjectType`のサブクラスとして定義されなければならないか、それらの関連フィールドを問い合わせした場合にエラーが表示されます。

```python
from graphene_django import DjangoObjectType
from .models import Category


class CategoryType(DjangoObjectType):
    class Meta:
        model = Category
        fields = ("foo",)
```

## デフォルトクエリセット

`DjangoObjectType`を使用している場合、独自の`get_queryset`メソッドを定義できます。
`Query`オブジェクトレベルの代わりに、`ObjectType`レベルでフィルタリングを制御するために、これを使用してください。

```python
from graphene_django import DjangoObjectType
from .models import Question


class QuestionType(DjangoObjectType):
    class Meta:
        model = Question

    @classmethod
    def get_queryset(cls, queryset, info):
        if info.context.user.is_anonymous:
            return queryset.filter(published=True)
        return queryset
```

## リゾルバー

GraphQLクエリが`Schema`オブジェクトに受け取られると、クエリに関連した**リゾルバー**にクエリをマッピングします。

このリゾルブメソッドは、次の形式でなければなりません。

```python
def resolve_foo(parent, info, **kwargs):
```

**foo**は、`Query`オブジェクト内で宣言されたフィールドの名前です。

```python
import graphene

from .models import Question
from .types import QuestionType


class Query(graphene.ObjectType):
    foo = graphene.List(QuestionType)

    def resolve_foo(root, info, **kwargs):
        id = kwargs.get("id")
        return Question.objects.get(id)
```

### 引数

さらに、リゾルバーは**フィールド定義で宣言された任意の引数**を受け取ります。
これは、GraphQLサーバーに入力引数を提供できるようにして、カスタムクエリで便利になります。

```python
import graphene

from .models import Question
from .types import QuestionType


class Query(graphene.ObjectType):
    question = graphene.Field(
        QuestionType,
        foo=graphene.String(),
        bar=graphene.Int()
    )

    def resolve_question(root, info, foo, bar):
        # もし、`foo`または`bar`がGraphQLクエリ内で宣言されている場合、それらはここにあり、
        # そうでない場合はNoneです。
        return Question.objects.filter(foo=foo, bar=bar).first()
```

### Info

すべてのリゾルブメソッドに渡される`info`引数は、なんらか役に立つ情報を持っています。
Graphene-Djangoのために、`info.context`属性は、Django開発者に慣れ親しんだ`HttpRequest`オブジェクトです。
これは、リゾルブメソッド内で、認証済みユーザーを確認するような、Djangoの`HttpRequest`の完全な機能を使用できるようにします。

```python
import graphene

from .models import Question
from .types import QuestionType


class Query(graphene.ObjectType):
    questions = graphene.List(QuestionType)

    def resolve_questions(root, info):
        # ユーザーが認証されているか確認します。
        if info.context.user.is_authenticated():
            return Question.objects.all()
        else:
            return Question.objects.none()
```

#### DjangoObjectType

定義された*DjangoObjectType*にマッピングされたリゾルバーは、クエリセットを返すメソッドのみで使用するべきです。
辞書を返す*values*のようなクエリセットのメソッドは、代わりに*defer*を使用してください。

## 単純なObjectType

Graphene-Djangoでは、Djangoモデルだけに限定されません。
カスタムフィールドを作成するために、または内部のDjangoモデルと外部API間の抽象化を提供するために、標準の`ObjectType`を使用できます。

```python
import graphene

from .models import Question


class MyQuestion(graphene.ObjectType):
    text = graphene.String()


class Query(graphene.ObjectType):
    question = graphene.Field(MyQuestion, question_id=graphene.String())

    def resolve_question(root, info, question_id):
        question = Question.objects.get(pk=question.id)
        return MyQuestion(
            text=question.question_text
        )
```

詳しい情報や例は、[grapheneのObjectType](https://docs.graphene-python.org/en/latest/types/objecttypes/)を参照してください。

## 完全な例

Relayをカスタマイズした例の詳細な情報は、grapheneの[Relayのドキュメント](https://docs.graphene-python.org/en/latest/relay/)を参照してください。

```python
from graphene import relay
from graphene_django import DjangoObjectType

from .models import Question

class QuestionType(DjangoObjectType):
    class Meta:
        model = Question
        interfaces = (relay.Node,)  # これを追加していることを確認してください。
        fields = "__all__"


class QuestionConnection(relay.Connection):
    class Meta:
        node = QuestionType


class Query:
    questions = relay.ConnectionField(QuestionConnection)

    def resolve_questions(root, info, **kwargs):
        return Question.objects.all()
```

これで、次のようなクエリを実行できます。

```graphql
{
  questions (first: 2, after: "YXJyYXljb25uZWN0aW9uOjEwNQ==") {
    pageInfo {
      startCursor
      endCursor
      hasNextPage
      hasPreviousPage
    }
    edges {
      cursor
      node {
        id
        questionText
      }
    }
  }
}
```

それは、次を返します。

```json
{
  "data": {
    "questions": {
      "pageInfo": {
        "startCursor": "YXJyYXljb25uZWN0aW9uOjEwNg==",
        "endCursor": "YXJyYXljb25uZWN0aW9uOjEwNw==",
        "hasNextPage": true,
        "hasPreviousPage": false
      },
      "edges": [
        {
          "cursor": "YXJyYXljb25uZWN0aW9uOjEwNg==",
          "node": {
            "id": "UGxhY2VUeXBlOjEwNw==",
            "question_text": "How did we get here?"
          }
        },
        {
          "cursor": "YXJyYXljb25uZWN0aW9uOjEwNw==",
          "node": {
            "id": "UGxhY2VUeXBlOjEwOA==",
            "name": "Where are we?"
          }
        }
      ]
    }
  }
}
```

`relay`は、`pageInfo`要素を追加して、ノードの`cursor`を含む`pagination`能力を自動的に実装することに注意してください。
これらの要素は、説明のために上記例に含まれています。

一般的なページ分けについて詳細に学ぶために、GraphQLコミュニティーサイトの[Pagination](https://graphql.org/learn/pagination/)を参照してください。
