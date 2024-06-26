# サブスクリプション

<https://docs.graphene-python.org/projects/django/en/latest/subscriptions/>

- [サブスクリプション](#サブスクリプション)

`graphene-django`プロジェクトは、現在GraphQLサブスクリプションをサポートしていません。
しかし、サブスクリプションのサポートを追加して、Webソケット上でサブスクリプション操作の実行をサポートするGraphiQLインターフェイスを提供する*コミュニテイ運営*のモジュールがいくつかあります。

GraphQLサブスクリプションのWebソケットベースのサポートを実装するために、次を行う必要があります。

- [django-channels](https://channels.readthedocs.io/en/latest/installation.html)のインストールと設定
- Webソケット上でサブスクリプションのサポートを追加する*サードパーティ*モジュールのインストールと追加
  - [graphql-python/graphql-ws](https://github.com/graphql-python/graphql-ws)
  - [datavance/django-channels-graphql-ws](https://github.com/datadvance/DjangoChannelsGraphqlWs)
  - [jaydenwindle/graphene-subscriptions](https://github.com/jaydenwindle/graphene-subscriptions)
- アプリケーションまたは少なくともGraphQLエンドポイントが、`django-channels`にビルトインされている[daphne](https://github.com/django/daphne)、[uvicorn](https://www.uvicorn.org/)、または[hypercorn](https://pgjones.gitlab.io/hypercorn/)のようなASGIプロトコルサーバーを通じて提供されることを確実にしてください。

> **⚠ 注意事項**
> デフォルトで、`graphene-django`に同梱されているGraphiQLインターフェイスは、任意の他の操作と同じパスでサブスクリプションを処理することを想定しています。
> 例えば、`/graphql`のような同じパスでGraphQL操作を処理するために、`urls.py`とお`routing.py`の両方を設定します。
> もしこれらのURLが異なる場合、に同梱されているGraphiQLインターフェイスはHTTPを介してサブスクリプションを実行することを試み、それはエラーを生成します。
> もしWebソケット接続を処理するために異なるURLを使用する必要がある場合、`settings.py`の`SUBSCRIPTION_PATH`を設定できます。
>
> ```python
> GRAPHENE = {
>     "SUBSCRIPTION_PATH": "/ws/graphql",
> }
> ```

> `routing.py`は`graphene-subscriptions`モジュールがエンドポイントの指定に使用する。

一度、サブスクリプションを処理するための適切な設定ができたら、任意の他の操作のように、サブスクリプションをテストするために、GraphiQLインターフェイスを使用できます。
