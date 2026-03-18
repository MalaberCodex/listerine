import SwiftUI

@main
struct ListerineApp: App {
    @StateObject private var authViewModel = AuthViewModel(
        urlStore: BackendURLStore(),
        passkeyService: PasskeyAuthService()
    )

    var body: some Scene {
        WindowGroup {
            RootView()
                .environmentObject(authViewModel)
        }
    }
}
