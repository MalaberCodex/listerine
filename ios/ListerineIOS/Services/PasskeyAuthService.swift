import AuthenticationServices
import Foundation

struct PasskeyResult {
    let username: String
    let backendURL: URL
    let operation: PasskeyOperation
    let summary: String
}

enum PasskeyOperation: String {
    case signUp = "Sign Up"
    case logIn = "Log In"
}

enum PasskeyAuthError: LocalizedError {
    case invalidUsername
    case unsupportedOperation

    var errorDescription: String? {
        switch self {
        case .invalidUsername:
            return "Enter an email or username before continuing."
        case .unsupportedOperation:
            return "Passkeys require iOS 16 or newer."
        }
    }
}

@MainActor
final class PasskeyAuthService: NSObject {
    func perform(
        operation: PasskeyOperation,
        username: String,
        backendURL: URL
    ) async throws -> PasskeyResult {
        let trimmedUsername = username.trimmingCharacters(in: .whitespacesAndNewlines)
        guard trimmedUsername.isEmpty == false else {
            throw PasskeyAuthError.invalidUsername
        }

        guard #available(iOS 16.0, *) else {
            throw PasskeyAuthError.unsupportedOperation
        }

        let relyingPartyIdentifier = backendURL.host ?? "localhost"
        let challenge = Data("listerine-placeholder-challenge".utf8)
        let userID = Data(trimmedUsername.utf8)
        let provider = ASAuthorizationPlatformPublicKeyCredentialProvider(
            relyingPartyIdentifier: relyingPartyIdentifier
        )

        switch operation {
        case .signUp:
            _ = provider.createCredentialRegistrationRequest(
                challenge: challenge,
                name: trimmedUsername,
                userID: userID
            )
        case .logIn:
            _ = provider.createCredentialAssertionRequest(challenge: challenge)
        }

        return PasskeyResult(
            username: trimmedUsername,
            backendURL: backendURL,
            operation: operation,
            summary: "Created a \(operation.rawValue.lowercased()) passkey request for \(trimmedUsername). Wire this request to \(backendURL.absoluteString) when backend passkey endpoints are ready."
        )
    }
}
