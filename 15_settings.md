# 設定

<https://docs.graphene-python.org/projects/django/en/latest/settings/>

- [設定](#設定)
  - [使用方法](#使用方法)
  - [SCHEMA](#schema)
  - [SCHEMA\_OUTPUT](#schema_output)
  - [SCHEMA\_INDENT](#schema_indent)
  - [MIDDLEWARE](#middleware)
  - [RELAY\_CONNECTION\_ENFORCE\_FIRST\_OR\_LAST](#relay_connection_enforce_first_or_last)
  - [RELAY\_CONNECTION\_MAX\_LIMIT](#relay_connection_max_limit)
  - [CAMELCASE\_ERRORS](#camelcase_errors)
  - [DJANGO\_CHOICE\_FIELD\_ENUM\_V3\_NAMING](#django_choice_field_enum_v3_naming)
  - [DJANGO\_CHOICE\_FIELD\_ENUM\_CUSTOM\_NAME](#django_choice_field_enum_custom_name)
  - [SUBSCRIPTION\_PATH](#subscription_path)
  - [GRAPHIQL\_HEADER\_EDITOR\_ENABLED](#graphiql_header_editor_enabled)

Graphene-Djangoは`settings`を使用してカスタマイズできます。
このページは、それぞれの設定とそれらのデフォルトを説明します。

## 使用方法

プロジェクトの`settings.py`に`GRAPHENE`という名前の辞書を作成して、Djangoプロジェクトに設定を追加します。

```python
GRAPHENE = {
  ...
}
```

## SCHEMA

最上位の`Schema`クラスの場所です。
デフォルトは`None`です。

```python
GRAPHENE = {
    "SCHEMA": "path.to.schema.schema",
}
```

## SCHEMA_OUTPUT

GraphQLスキーマを出力するファイルの名前です。
デフォルトは`schema.json`です。

```python
GRAPHENE = {
    "SCHEMA_OUTPUT": "data/schema.json",
}
```

## SCHEMA_INDENT

スキーマを出力するときのインデントのレベルです。
デフォルトは`2`です。

```python
GRAPHENE = {
    "SCHEMA_INDENT": 2,
}
```

## MIDDLEWARE

それぞれのGraphQLクエリで実行されるミドルウェアのタプルです。
より詳細は[ミドルウェア](https://docs.graphene-python.org/en/latest/execution/middleware/)を参照してください。
デフォルトは`()`です。

```python
GRAPHENE = {
    "MIDDLEWARE": (
        "path.to.my.middleware.class",
    ),
}
```

## RELAY_CONNECTION_ENFORCE_FIRST_OR_LAST

`first`または`last`引数を持つようにrelayクエリを強制します。
デフォルトは`False`です。

```python
GRAPHENE = {
    "RELAY_CONNECTION_ENFORCE_FIRST_OR_LAST": False,
}
```

## RELAY_CONNECTION_MAX_LIMIT

relayコネクションを介してリクエストできるオブジェクトの最大数です。
デフォルトは`100`です。

```python
GRAPHENE = {
    "RELAY_CONNECTION_MAX_LIMIT": 100,
}
```

## CAMELCASE_ERRORS

`True`に設定したとき、エラーオブジェクト内のフィールド名がキャメルケースになります。
デフォルトでそれらはスネークケースです。
デフォルトは`False`です。

```python
GRAPHENE = {
    "CAMELCASE_ERRORS": False,
}

# result = schema.execute(...)
# print(result.errors)
# [
#   {
#     'field': 'test_field',
#     'messages': ['This field is required.'],
#   }
# ]
```

```python
GRAPHENE = {
    "CAMELCASE_ERRORS": True,
}

# result = schema.execute(...)
# print(result.errors)
# [
#   {
#     'field': 'testField',
#     'messages': ['This field is required.'],
#   }
# ]
```

## DJANGO_CHOICE_FIELD_ENUM_V3_NAMING

Django選択フィールドから自動的に生成されるEnum型に新しい名前付け書式を使用するために`True`を設定します。
その新しい書式は、次のようになります。

```text
{app_label}{object_name}{field_name}Choices
```

デフォルトは`False`です。

## DJANGO_CHOICE_FIELD_ENUM_CUSTOM_NAME

Django選択フィールドを受け取り、Enum型の名前付けを完全にカスタマイズする文字列を返す関数のパスを定義します。
もし関数が設定された場合、`DJANGO_CHOICE_FIELD_ENUM_V3_NAMING`設定は無視されます。
デフォルトは`None`です。

```python
# myapp.utils
def enum_naming(field):
    if isinstance(field.model, User):
        return f"CustomUserEnum{field.name.title()}"
    return f"CustomEnum{field.name.title()}"


# settings.py
GRAPHENE = {
    "DJANGO_CHOICE_FIELD_ENUM_CUSTOM_NAME": "myapp.utils.enum_naming",
}
```

## SUBSCRIPTION_PATH

サブスクリプション操作がルーティングされる代わりのURLパスを定義します。

GraphiQLインターフェイスは、サブスクリプション操作を賢くルーティングするためにこの設定を使用します。
これは、例えば、WSGIサーバーが`/graphql`でリスニングして、ASGIサーバーが`/ws/graphql`でリスニングする場合など、同じパスをWebソケットが処理されることを避ける、より高度なインフラストラクチャー要件がある場合に便利です。
デフォルトは`None`です。

```python
GRAPHENE = {
    "SUBSCRIPTION_PATH": "/ws/graphql",
}
```

## GRAPHIQL_HEADER_EDITOR_ENABLED

GraphiQLバーション1.0.0移行では、クエリ変数と同じような手法でカスタムヘッダーを設定できます。
何らかの理由でGraphiQLヘッダの編集を無効にしたい場合は`False`を設定してください。
この設定は、GraphiQLオプションの`headerEditorEnabled`に渡され、その詳細は[GraphiQLドキュメント](https://github.com/graphql/graphiql/tree/main/packages/graphiql#options)を参照してください。
デフォルトは`True`です。

```python
GRAPHENE = {
    "GRAPHIQL_HEADER_EDITOR_ENABLED": True,
}
```
