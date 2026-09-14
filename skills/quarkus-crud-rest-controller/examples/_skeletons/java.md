# Resource class skeleton (Java)

## Code

```java
package {packageName};

import jakarta.ws.rs.Path;

@Path("{requestPath}")
public class {className} {

}
```

## Variables
| Variable | Source | Default |
|----------|--------|---------|
| `{packageName}` | project context | same package as existing resources, else `mainPackage` |
| `{className}` | user choice | `{EntityName}Resource` |
| `{requestPath}` | basePath + resourcePath | `/api/{entityVarPlural}` |
