# JsonWebToken injection fragment (Java)

## Insert Point
As an injected field in a resource/service that already exists.

## Code

```java
// primary token of the flow (access token in bearer mode, ID token in the code flow)
@jakarta.inject.Inject
org.eclipse.microprofile.jwt.JsonWebToken jwt;

// usage
String subject = jwt.getSubject();
String email = jwt.getClaim("${claimName}");
java.util.Set<String> groups = jwt.getGroups();

// code flow only -- inject the ID token specifically
@jakarta.inject.Inject
@io.quarkus.oidc.IdToken
org.eclipse.microprofile.jwt.JsonWebToken idToken;
```

## Variables
| Variable | Source | Default |
|----------|--------|---------|
| `${claimName}` | user input | skip the claim example when not needed |

## Notes
- `JsonWebToken` is `org.eclipse.microprofile.jwt.JsonWebToken`; `@IdToken` is `io.quarkus.oidc.IdToken`
  and applies to the web-app variant only — extract both into imports.
- Do not add this fragment just because authentication is configured; inject the token only when the
  code needs claims.
