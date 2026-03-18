import Foundation

@MainActor
final class AuthViewModel: ObservableObject {
    @Published var backendURLInput = ""
    @Published var username = ""
    @Published var configuration: AppConfiguration
    @Published var isPerformingPasskeyRequest = false
    @Published var latestStatusMessage = ""
    @Published var errorMessage: String?

    private let urlStore: BackendURLStoring
    private let passkeyService: PasskeyAuthService

    init(urlStore: BackendURLStoring, passkeyService: PasskeyAuthService) {
        self.urlStore = urlStore
        self.passkeyService = passkeyService

        let loadedConfiguration = urlStore.load()
        configuration = loadedConfiguration
        backendURLInput = loadedConfiguration.backendURL?.absoluteString ?? ""
    }

    var backendURLDescription: String {
        configuration.backendURL?.absoluteString ?? "Not configured"
    }

    func saveBackendURL() {
        do {
            configuration = try urlStore.save(backendURLString: backendURLInput)
            backendURLInput = configuration.backendURL?.absoluteString ?? backendURLInput
            latestStatusMessage = "Backend URL saved."
            errorMessage = nil
        } catch {
            errorMessage = error.localizedDescription
        }
    }

    func resetBackendURL() {
        urlStore.clear()
        configuration = AppConfiguration(backendURL: nil)
        backendURLInput = ""
        latestStatusMessage = "Backend URL cleared."
        errorMessage = nil
    }

    func performPasskey(_ operation: PasskeyOperation) async {
        guard let backendURL = configuration.backendURL else {
            errorMessage = "Set your backend URL before using passkeys."
            return
        }

        isPerformingPasskeyRequest = true
        errorMessage = nil
        defer { isPerformingPasskeyRequest = false }

        do {
            let result = try await passkeyService.perform(
                operation: operation,
                username: username,
                backendURL: backendURL
            )
            latestStatusMessage = result.summary
        } catch {
            errorMessage = error.localizedDescription
        }
    }
}
