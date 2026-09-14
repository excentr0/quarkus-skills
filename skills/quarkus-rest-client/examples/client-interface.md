# REST client interface (Java)

## Code

### skeleton
```java
package ${packageName};

import jakarta.ws.rs.GET;
import jakarta.ws.rs.POST;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.PathParam;
import org.eclipse.microprofile.rest.client.inject.RegisterRestClient;

@Path("${remoteBasePath}")
@RegisterRestClient(configKey = "${configKey}")
public interface ${ClientName} {

}
```

### method — GET one resource
```java
@GET
@Path("/${resourcePath}/{id}")
${DtoFqn} getById(@PathParam("id") ${IdType} id);
```

### method — POST create
```java
@POST
@Path("/${resourcePath}")
${DtoFqn} create(${DtoFqn} ${bodyVar});
```

### method — status-only operation
```java
@DELETE
@Path("/${resourcePath}/{id}")
jakarta.ws.rs.core.Response delete(@PathParam("id") ${IdType} id);
```

### method — per-invocation URL override
```java
@GET
@Path("/${resourcePath}/{id}")
${DtoFqn} getByIdFrom(@PathParam("id") ${IdType} id, @io.quarkus.rest.client.reactive.Url String ${baseUrlParam});
```

## Variables
| Variable | Source | Default |
|----------|--------|---------|
| `${packageName}` | project context | package of existing clients, else `{mainPackage}.client` |
| `${ClientName}` | user choice | `{ServiceName}Client` |
| `${configKey}` | user choice | kebab-case service name, e.g. `billing-api` |
| `${remoteBasePath}` | API docs | omit the `@Path` annotation when the API has no common base path |
| `${resourcePath}` | API docs | remote resource path, e.g. `invoices` |
| `${DtoFqn}` | project DTOs | record from the project's DTO package |
| `${IdType}` | API docs | `String` for external ids, `Long` for ids mirrored from the local model |
| `${bodyVar}` | — | decapitalized DTO name |
| `${baseUrlParam}` | — | parameter name for the per-invocation URL (`baseUrl`) — only for follow-the-pointer scenarios; prefer config for normal calls |

## Notes
- Omit `@Path` entirely when the service has no common base path; annotate each method with its
  full path instead.
- The import list must cover every shortened name used in the body — do not leave FQN usages in
  method fragments without imports or vice versa.
- Only methods for operations confirmed in Step 2 — never scaffold the full hypothetical API.
