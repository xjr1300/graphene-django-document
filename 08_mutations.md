# ミューテーション

<https://docs.graphene-python.org/projects/django/en/latest/mutations/>

- [ミューテーション](#ミューテーション)
  - [イントロダクション](#イントロダクション)
  - [単純な例](#単純な例)
  - [Djangoフォーム](#djangoフォーム)
    - [DjangoFormMutation](#djangoformmutation)
    - [DjangoModelFormMutation](#djangomodelformmutation)
    - [フォームの検証](#フォームの検証)
  - [Django REST Framework](#django-rest-framework)
    - [作成／更新操作](#作成更新操作)
    - [更新クエリのオーバーライド](#更新クエリのオーバーライド)
  - [Relay](#relay)
  - [Djangoデータベーストランザクション](#djangoデータベーストランザクション)
    - [HTTPリクエストへの尾トランザクションを試行する](#httpリクエストへの尾トランザクションを試行する)
    - [ミューテーションでトランザクションを試行する](#ミューテーションでトランザクションを試行する)

## イントロダクション

Graphene-Djangoは、ミューテーションを実行することを簡単にします。

Graphene-Djangoを使用して、素早くCRUD機能を構築するために、Djangoプロジェクトにカスタムミューテーションを追加するために、[grapheneのミューテーション](https://docs.graphene-python.org/en/latest/types/mutations/)機能を使用する一方で、事前に存在するDjangoの機能を活用できます。

## 単純な例

```python
import graphene
from graphene_django import DjangoObjectType

from .models import Question


class QuestionType(DjangoObjectType):
    class Meta:
        model = Question


class QuestionMutation(graphene.Mutation):
    class Arguments:
        # このミューテーションの入力引数
        text = graphene.String(required=True)
        id = graphene.ID()

    # このクラス属性はミューテーションのレスポンスを定義します。
    question = graphene.Field(QuestionType)

    @classmethod
    def mutate(cls, root, info, text, id):
        question = Question.objects.get(pk=id)
        question.text = text
        question.save()
        # このミューテーションのインスタンスを返すことに注意してください。
        return QuestionMutation(question=question)


class Mutation(graphene.ObjectType):
    update_question = QuestionMutation.Field()
```

## Djangoフォーム

Graphene-Djangoは、Djangoフォームのフィールドをミューテーションの入力に変換するミューテーションクラスを備えています。

### DjangoFormMutation

```python
from graphene_django.forms.mutation import DjangoFormMutation


class MyForm(forms.Form);
    name = forms.CharField()


class MyMutation(DjangoFormMutation):
    class Meta:
        form_class = MyForm
```

`MyMutation`は、自動的に`input`引数を受け取ります。
この引数は、キーが`name`で、値が文字列である`dict`になります。

### DjangoModelFormMutation

`DjangoModelFormMutation`は、`ModelForm`からフィールドを引き出します。

```python
import graphene
from graphene_django.forms.mutation import DjangoModelFormMutation


class Pet(models.Model):
    name = models.CharField()


class PetForm(forms.ModelForm):
    class Meta:
        model = Pet
        fields = ("name",)


# ミューテーションが成功で完了したとき、これが返されます。
class PetType(DjangoObjectType):
    class Meta:
        model = Pet


class PetMutation(DjangoModelFormMutation):
    pet = graphene.Field(PetType)

    class Meta:
        form_class = PetForm
```

`PetMutation`は、`PetForm`からフィールドを取得して、それらを入力に変えます。
もじ、フォームが妥当な場合、ミューテーションが`Pet`モデルの`DjangoObjectType`を検索して、それを`pet`キーを下に返します。
そうでない場合、それは、エラーのリストを返します。

入力名（デフォルトは`input`）と返されるフィールド名（デフォルトは小文字のモデル名）を変更できます。

```python
class PetMutation(DjangoModelFormMutation):
    class Meta:
        form_class = PetForm
        input_field_name = "data"
        return_field_name = "my_pet"
```

### フォームの検証

フォームミューテーションは、フォームの`id_valid()`を呼び出します。

もし、フォームが妥当であれば、ミューテーションの`perform_mutate(form, info)`クラスメソッドが呼び出されます。
フォームを保存する方法を変更する、または異なるGrapheneオブジェクトタイプを返す場合は、このメソッドをオーバーライドしてください。

もし、フォームが妥当でない場合は、エラーのリストが返されます。
これらのエラーは2つのフィールドがあります。
`field`は不正なフォームフィールドの名前を含む文字列で、`messages`は検証メッセージのリストです。

## Django REST Framework

Graphene-DjangoのミューテーションでDjango REST Frameworkのシリアライザーを再利用できます。

*SerializerMutation基本クラス*を使用して、ミューテーションを基礎としたシリアライザーを作成できます。

```python
from graphene_django.rest_framework.mutation import SerializerMutation


class MyAwesomeMutation(SerializerMutation):
    class Meta:
        serializer_class = MySerializer
```

### 作成／更新操作

デフォルトで`ModelSerializer`は作成と更新操作を受け付けます。
これをカスタマイズするために、`SerializerMutation`クラスの`model_operations`属性を使用します。

更新操作は、デフォルトで主キーによってモデルを検索します。
`SerializerMutation`クラスの`lookup_field`属性で検索をカスタマイズできます。

```python
from graphene_django.rest_framework.mutation import SerializerMutation

from .serializer import MyModelSerializer


class AwesomeModelMutation(SerializerMutation):
    class Meta:
        serializer_class = MyModelSerializer
        model_operations = ["create", "update"]
        lookup_field = 'id'
```

### 更新クエリのオーバーライド

更新を適用する方法をオーバーライドするために、`get_serializer_kwargs`メソッドを使用してください。

```python
from graphene_django.rest_framework.mutation import SerializerMutation

from .serializers import MyModelSerializer


class AwesomeModelMutation(SerializerMutation):
    class Meta:
        serializer_class = MyModelSerializer

    @classmethod
    def get_serializer_kwargs(cls, root, info, **input):
        if "id" in input:
            instance = Post.objects.filter(
                id=input["id"],
                owner=info.context.user,
            ).first()
            if instance:
                return {
                    "instance": instance,
                    "data": input,
                    "partial": True,
                }
            else:
                return http.Http.404
        return {"data": input, partial: True}
```

## Relay

ミューテーションでRelayを使用できます。
Relayのミューテーションは、`ClientIDMutation`から派生して、`mutate_and_get_payload`メソッドを実装する必要があります。

```python
import graphene
from graphene import relay
from graphene_django import DjangoObjectType
from graphql_relay import from_global_id

from .queries import QuestionType


class QuestionMutation(relay.ClientIDMutation):
    class Input:
        text = graphene.String(required=True)
        id = graphene.ID()

    question = graphene.Field(QuestionType)

    @classmethod
    def mutate_and_get_payload(cls, root, info, text, id):
        question = Question.objects.get(pk=from_global_id(id)[1])
        question.text = text
        question.save()
        return QuestionMutation(question=question)
```

> `graphql_relay`の`from_global_id`関数は、`to_global_id`関数で作成されたグローバルIDを受け取り、それを作成するために使用する型名とIDを返す。
> `from_global_id`関数は、型名とIDを`NamedTuple`で返し、そのフィールドの名前と型は順に`type(str)`、`id(str)`である。
> `to_global_id`関数は、型の名前(str)とID(Union[str, int])を受け取り、すべての型の間で一意となるグローバルIDを返す。
> `to_global_id`関数は、`f"{type_name}:{GraphQLID.serialize(id)}"`で生成した文字列をbase64でエンコードした文字列を、グローバルIDとして返す。
> `GraphQLID.serialize(id)`は、単純に`id`を文字列に変換した値を返す。

relayにおいて`class Arguments`が`class Input`に名前が変更されていることに注意してください。
このため、graphene 2.0で`class Arguments`は非推奨です。

`relay.ClientIDMutation`は、`clientIDMutation`引数を受け取ります。
また、この引数は、ミューテーションの結果としてクライアントに戻されます（何もする必要はありません）。
多くのGraphQLリクエストをプールして管理するサービスのために、`clientIDMutation`は、特定のミューテーションとレスポンスをマッチングさせます。

## Djangoデータベーストランザクション

Djangoは、データベーストランザクションを管理する方法をいくつか提供しています。

### HTTPリクエストへの尾トランザクションを試行する

Djangoでトランザクションを処理する一般的な方法は、それぞれのリクエストをトランザクションでラップすることです。
それをしたいそれぞれのデータベースの設定で、`ATOMIC_REQUESTS`を`True`に設定することは、この振る舞いを有効にします。

トランザクションは次のように機能します。
`GraphQLView`を呼び出す前にDjangoはトランザクションを開始します。
もし、問題なくレスポンスが生成された場合、Djangoはそのトランザクションをコミットします。
もし、`DjangoFromMutation`または`DjangoModelFormMutation`のようなビューが例外を生成した場合、Djangoはそのトランザクションをロールバックします。

> **⚠ 警告**
> このトランザクションモデルの単純さは魅力的な一方で、そうれはトラフィックが増加したとき非効率になります。
> すべてのリクエストでトランザクションを開始することは、何らかのオーバーヘッドがあります。
> 性能の影響はアプリケーションのクエリパターンと、データベースがロックを処理する方法に依存します。

### ミューテーションでトランザクションを試行する

ミューテーションは、クエリとちょうど同様に、複数のフィールドを含むことができます。
名前の他にクエリとミューテーションの間に重要な違いが1つあります。

***並列でクエリのフィールドは実行される一方で、ミューテーションのフィールドは次々順番に実行されます。***

これは、もし、1つのリクエストで2つの`incrementCredits`ミューテーションを送信した場合、2つ目が開始される前に1つ目が完了することを保証されることを意味しており、それら自身で競合状態にならないことを確実にします。

一方、1つ目の`incrementCredits`は成功したが、2つ目は失敗した場合、このままでは操作を再試行できません。
これが、トランザクション内ですべてのミューテーションフィールドを実行することは良い考えである理由で、すべて発生するか何も発生しないかを保証します。

すべてのデータベースでこの振る舞いを有効にするために、設定ファイルでgrapheneの`ATOMIC_MUTATIONS`設定を`True`に設定してください。

```python
GRAPHENE = {
    "ATOMIC_MUTATIONS": True,
}
```

そうではなく、特定のデータベースに対してこの振る舞いを有効にしたい場合、データベース設定の`ATOMIC_MUTATIONS`を`True`に設定してください。

```python
DATABASES = {
    "default": {
        "ATOMIC_MUTATIONS": True,
    }
}
```

ここで、次のミューテーション例を与えます。

```graphql
mutation IncreaseCreditsTwice {
  increaseCredits1: increaseCredits(input: { amount: 10 }) {
    balance
    errors {
      field
      messages
    }
  }
  increaseCredits2: increaseCredits(input: { amount: -1 }) {
    balance
    errors {
      field
      messages
    }
  }
}
```

サーバーは次を返します。

```json
{
  "data": {
    "increaseCredits1": {
      "balance": 10.0,
      "errors": []
    },
    "increaseCredits2": {
      "balance": null,
      "errors": [
        {
          "field": "amount",
          "message": "Amount should be a positive number"
        }
      ]
    },
  }
}
```

しかし、残高は変わりません。
