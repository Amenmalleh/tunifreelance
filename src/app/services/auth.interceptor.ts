import { HttpInterceptorFn, HttpErrorResponse } from '@angular/common/http';
import { inject } from '@angular/core';
import { AuthService } from './auth.service';
import { catchError } from 'rxjs/operators';
import { switchMap } from 'rxjs/operators';
import { throwError } from 'rxjs';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const auth = inject(AuthService);
  const token = auth.accessToken();
  const isRefreshRequest = req.url.endsWith('/token/refresh/');
  const canAttemptRefresh = !isRefreshRequest && auth.hasRefreshToken();

  if (token && !isRefreshRequest) {
    // Only add token if it looks like a valid JWT (has 3 parts separated by dots)
    if (token.split('.').length === 3) {
      req = req.clone({
        setHeaders: {
          Authorization: `Bearer ${token}`
        }
      });
    }
  }

  if (!token && canAttemptRefresh) {
    return auth.refreshAccessToken().pipe(
      switchMap((newAccessToken) => {
        const authenticatedRequest = req.clone({
          setHeaders: {
            Authorization: `Bearer ${newAccessToken}`
          }
        });
        return next(authenticatedRequest);
      }),
      catchError((error: HttpErrorResponse) => throwError(() => error))
    );
  }

  return next(req).pipe(
    catchError((error: HttpErrorResponse) => {
      if (
        !isRefreshRequest &&
        error.status === 401 &&
        token &&
        error.error?.code === 'token_not_valid'
      ) {
        return auth.refreshAccessToken().pipe(
          switchMap((newAccessToken) => {
            const retriedRequest = req.clone({
              setHeaders: {
                Authorization: `Bearer ${newAccessToken}`
              }
            });
            return next(retriedRequest);
          })
        );
      }

      return throwError(() => error);
    })
  );
};
