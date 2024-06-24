# スキーマ

<https://docs.graphene-python.org/projects/django/en/latest/schema/>

- [スキーマ](#スキーマ)
  - [スキーマを追加する](#スキーマを追加する)

`graphene.Schema`オブジェクトは、データモデルを説明して、データを取得する方法を理解する関連したリゾルブメソッドの集合をGraphQLサーバーに提供します。
作成できる最も基本的なスキーマは次の用になります。

```python
import graphene


class Query(graphene.ObjectType):
    pass


class Mutation(graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
```

スキーマは何もしませんが、新しい`Query`または`Mutation`フィールドを受け付ける準備ができています。

## スキーマを追加する

`Query`と`Mutation`を実装した場合、スキーマでそれらを登録できます。

```python
import graphene

import my_app.schema.Query
import my_app.schema.Mutation


class Query(my_app.schema.Query, # ここでQueryオブジェクトを追加してください。
            graphene.ObjectType
):
    pass


class Mutation(my_app.schema.Mutation, # ここでMutationオブジェクトを追加してください。
               graphene.ObjectType
):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
```

好みに応じて、基本的な`Query`と`Mutation`に多くのミックスインを追加できます。

スキーマについての詳細は[コアgrapheneドキュメント](https://docs.graphene-python.org/en/latest/types/schema/)を参照してください。
