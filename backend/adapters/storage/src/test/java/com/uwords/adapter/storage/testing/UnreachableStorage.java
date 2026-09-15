package com.uwords.adapter.storage.testing;

import jakarta.persistence.EntityManager;
import jakarta.persistence.PersistenceException;
import java.sql.SQLException;
import javax.sql.DataSource;
import org.mockito.ArgumentMatchers;
import org.mockito.Mockito;

public final class UnreachableStorage {

    public static final String CONNECTION_REFUSED = "connection refused";

    private UnreachableStorage() {
    }

    public static EntityManager entityManager() {
        EntityManager entityManager = Mockito.mock(EntityManager.class);
        Mockito.when(entityManager.find(ArgumentMatchers.<Class<Object>>any(), ArgumentMatchers.any()))
                .thenThrow(new PersistenceException(CONNECTION_REFUSED));
        return entityManager;
    }

    public static DataSource dataSource() throws SQLException {
        DataSource dataSource = Mockito.mock(DataSource.class);
        Mockito.when(dataSource.getConnection()).thenThrow(new SQLException(CONNECTION_REFUSED));
        return dataSource;
    }
}
