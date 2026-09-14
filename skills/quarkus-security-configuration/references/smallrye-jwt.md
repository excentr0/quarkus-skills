# MP-JWT Variant (quarkus-smallrye-jwt)

Authentication type: `MP_JWT` — legacy MicroProfile JWT verification: tokens are verified locally
against a public key and an issuer, with no OIDC discovery or session handling.

**Prefer the OIDC variants for new applications.** Use this variant only when the project already
uses `quarkus-smallrye-jwt`, or when the user explicitly wants local public-key verification
without an OIDC provider connection.

## Property blocks used

- `examples/_properties/smallrye-jwt/properties.md` (all blocks)

## Annotation fragments used

- `examples/_annotations/authenticated-and-permit/java.md`
- `examples/_annotations/roles-allowed/java.md` — when role restrictions were requested
- `examples/_annotations/identity-injection/java.md` — when the caller's name/roles are needed in code
- `examples/_annotations/jwt-injection/java.md` — when token claims are needed in code

## Dependencies

- `examples/_dependencies/smallrye-jwt.md`

## Questions

Ask only what Step 0/1 did not already answer.

### Token verification (plain text)

```text
Public key location (file, classpath resource, or URL)? []
Issuer? []
```

Both are mandatory for verification — ask for them; do not invent values.

### Path permissions

Ask the two questions from `references/common-rules.md` → Path permissions. Same defaults:
`/*` → `authenticated`, no public paths, no role policy unless requested.

## Generation

1. Read `examples/_properties/smallrye-jwt/properties.md`.
2. Write the verification block:
   - `%prod.mp.jwt.verify.publickey.location=<location>`
   - `%prod.mp.jwt.verify.issuer=<issuer>`
   - If the project uses Dev Services for Keycloak in dev/test, mention the commented
     `%dev.` block with `${keycloak.url}` — do not enable it unless the user confirms Dev Services.
3. Write the permission blocks: `/*` → `authenticated` (default), plus a `permit` set for public
   paths if any.
4. Apply annotation fragments to the targeted resources.
5. Add dependencies from `examples/_dependencies/smallrye-jwt.md` for artifacts not already present
   (prefer `./mvnw quarkus:add-extension -Dextensions="quarkus-smallrye-jwt,quarkus-security"` /
   `./gradlew addExtension --extensions="quarkus-smallrye-jwt,quarkus-security"`).
6. Report: property keys written, permission rules, annotations applied.

## Notes

- Verification is local: signature by `publickey.location`, claims by `mp.jwt.verify.issuer`. There
  is no provider discovery document and no token endpoint.
- Roles: MP-JWT maps the token `groups` claim to roles by default. If the tokens carry roles in a
  different claim, check the SmallRye JWT documentation for the claim-path property — do not invent
  a property name.
- No session, no login page, no logout config in this variant.
- If the user asks for provider discovery, login flows, or logout — that is the OIDC variants'
  territory; suggest switching instead of extending this config.
