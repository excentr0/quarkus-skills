# Injecting and using the client (Java)

## Insert Point
Consumer class body — a service or resource that calls the client.

## Code

### service (constructor injection)
```java
package ${packageName};

import jakarta.enterprise.context.ApplicationScoped;
import org.eclipse.microprofile.rest.client.inject.RestClient;

@ApplicationScoped
public class ${ConsumerClassName} {

    private final ${ClientName} ${clientVar};

    public ${ConsumerClassName}(@RestClient ${ClientName} ${clientVar}) {
        this.${clientVar} = ${clientVar};
    }

    ${ResponseFqn} ${consumerMethodName}(${RequestFqn} ${requestVar}) {
        return ${clientVar}.${operationMethod}(${requestVar});
    }
}
```

### resource (method with a path parameter)
```java
package ${packageName};

import jakarta.enterprise.context.ApplicationScoped;
import jakarta.ws.rs.GET;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.PathParam;
import jakarta.ws.rs.Produces;
import jakarta.ws.rs.core.MediaType;
import org.eclipse.microprofile.rest.client.inject.RestClient;

@Path("/${resourcePath}")
@ApplicationScoped
public class ${ResourceName} {

    private final ${ClientName} ${clientVar};

    public ${ResourceName}(@RestClient ${ClientName} ${clientVar}) {
        this.${clientVar} = ${clientVar};
    }

    @GET
    @Path("/{id}")
    @Produces(MediaType.APPLICATION_JSON)
    public ${DtoFqn} ${resourceMethodName}(@PathParam("id") ${IdType} id) {
        return ${clientVar}.getById(id);
    }
}
```

## Variables
| Variable | Source | Default |
|----------|--------|---------|
| `${packageName}` | project context | package of the consumer class |
| `${ConsumerClassName}` | project context | `{ServiceName}Service` |
| `${ResourceName}` | project context | `{EntityName}Resource` (see `quarkus-crud-rest-controller`) |
| `${ClientName}` | Step 4 | `{ServiceName}Client` |
| `${clientVar}` | — | decapitalized client name |
| `${operationMethod}` | Step 4 | method name from the client interface |
| `${consumerMethodName}` / `${resourceMethodName}` | project verb convention | mirrors the operation |
| `${RequestFqn}` / `${ResponseFqn}` / `${DtoFqn}` | project DTOs | record types |
| `${IdType}` | Step 4 | matches the client interface |
| `${requestVar}` | — | decapitalized request DTO name |

## Notes
- The `@RestClient` qualifier is mandatory at the injection point — without it CDI does not know
  which client bean to inject.
- Quarkus generates the no-args constructor and, with a single constructor, `@Inject` is not
  required — plain constructor injection is the project-consistent style.
- Never inject one client into another client interface; compose at the service layer.
- Client exceptions (`jakarta.ws.rs.WebApplicationException` for status ≥ 400 by default) should be
  wrapped or mapped only the way the project already does it.
