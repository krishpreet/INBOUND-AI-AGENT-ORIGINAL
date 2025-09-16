from app.telephony.provider_registry import get_provider

def main():
    provider = get_provider()
    print(f"Active Provider: {provider.name}")

if __name__ == "__main__":
    main()

