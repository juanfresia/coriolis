#include "PointOfSale.h"
#include <sstream>
#include <utils/ConcuMath.h>

// @has_checkpoints

static const char * pointOfSalesNames[] = {
        "Carrefour",
        "Viveros Alvarez Windey",
        "Robles Viveros, somos madera buena",
        "Lopez Viveros Fis Fis",
        "Coto (Yo te Conozco)",
        "Viveros Dia (si no compras flores es porque queres)",
        "Vivan los Viveros",
        "Kiosco de Diarios y Flores",
        "Flores Concurrentes",
        "Flores No Starvation",
        "Critical flowers section"
};

#define POFS_NAMES_AMOUNT 11

PointOfSale::PointOfSale(unsigned int id, std::string name, Pipe & pr, std::vector<internet_order_t> orders) :
    id(id),
    name(name),
    pipeWithManagerRead(pr),
    protocol(CHANNEL_POINT_OF_SALE_MANAGER, NAMED_PIPE_WRITE),
    logPipe(LOG_WRITE, E_POINT_OF_SALE) {

    this->orders = orders;
}

PointOfSale::~PointOfSale() {}

std::string PointOfSale::describe() const {
    std::stringstream ss;
    ss << this->name << " (ID: " << this->id << ")";
    return ss.str();
}

std::string PointOfSale::randName(void) {
    const char * name = pointOfSalesNames[ConcuMath::getRandomInt(0, POFS_NAMES_AMOUNT - 1)];
    return std::string(name);
}

void PointOfSale::start() {
    bool quit = false;

    while (!quit) {
        // Wait for manager response
        logPipe << this->describe() << " waiting for event" << END_LINE;
        event_t event = this->protocol.getEventType(this->pipeWithManagerRead);
        logPipe << this->describe() << " received event: '" << event << "'" << END_LINE;

        if (event == EVENT_USER) {

            logPipe << this->describe() << " received user event, waiting for user action" << END_LINE;
            action_t action = this->protocol.getAction(this->pipeWithManagerRead);
            logPipe << this->describe() << " received action: '" << action << "'" << END_LINE;

            switch (action) {
                case ACTION_CONTINUE: {
                    continue;
                }

                case ACTION_PAUSE: {
                    this->pause(&quit);
                    break;
                }

                case ACTION_RESUME: {
                    // Ignore if it is not paused
                    break;
                }

                case ACTION_QUIT: {
                    quit = true;
                    break;
                }

                default: {
                    logPipe << this->name << " (ID: " << this->id << ") does not know action: '" << action << "'"
                            << END_LINE;
                }
            }
        }

        if (event == EVENT_CLASSIFIED_PACKAGE) {
            logPipe << "New package arrived to point of sale: " << this->describe() << END_LINE;
            distribution_id distributionId;
            std::vector<Flower> package = this->protocol.receiveClassifiedFlowersPackage(&distributionId, this->pipeWithManagerRead);
            logPipe << this->describe() << " received package with: " << package.size() << " number of flowers" << END_LINE;
            // @checkpoint sp_receive_package this->id package.front().getFlowerId() package.front().getFlowerName()

            this->updateStocks(package);
            this->deliverInternetOrders();
        }

        if (event == EVENT_BUY_ORDER) {
            Order order = this->protocol.receiveOrder(this->pipeWithManagerRead);
            logPipe << "Received a buy order from client: " << order.describe() << END_LINE;
            this->deliverLocalOrder(order);
        }

    }

    logPipe << this->describe() << " will quit" << END_LINE;
    exit(0);
}

void PointOfSale::pause(bool * quit) {
    logPipe << this->describe() << " is paused" << END_LINE;
    action_t action = this->protocol.getAction(this->pipeWithManagerRead);

    switch (action) {
        case ACTION_RESUME: {
            logPipe << this->describe() << " will resume" << END_LINE;
            return;
        }

        case ACTION_QUIT: {
            *quit = true;
            return;
        }

        default:
            this->pause(quit);
    }
}

void PointOfSale::updateStocks(std::vector<Flower> &package) {
    logPipe << this->describe() << " updating the stocks " << END_LINE;
    flower_t type = package.front().getType();
    for (Flower & flower: package) {
        // @checkpoint sp_unpackage_bouquet this->id flower.getFlowerId() package.front().getFlowerId() flower.getFlowerName() 
    }

    switch (type) {
        case FLOWER_ROSE:
            logPipe << this->describe() << " updating roses stock " << END_LINE;
            // Append
            this->rosesStock.insert(std::end(this->rosesStock), std::begin(package), std::end(package));
            break;

        case FLOWER_TULIP:
            logPipe << this->describe() << " updating tulips stock " << END_LINE;
            this->tulipsStock.insert(std::end(this->tulipsStock), std::begin(package), std::end(package));
            break;

        default:
            logPipe << this->describe() << " does not store flowers of type: " << type << END_LINE;
    }
}

void PointOfSale::deliverInternetOrders(void) {

    // Check if there is any remaining order
    if (this->orders.size() == 0) {
        logPipe << this->describe() << " has not any remaining internet order" << END_LINE;
        return;
    }

    logPipe << this->describe() << " will try to deliver remaining internet orders" << END_LINE;
    std::vector<internet_order_t>::iterator it = this->orders.begin();

    while (it != this->orders.end()) {
        // Check stocks
        logPipe << this->describe() << " checking stocks for " << it->roses << " roses and " << it->tulips << " tulips" << END_LINE;
        if (it->tulips <= this->tulipsStock.size() && it->roses <= this->rosesStock.size()) {
            // Creates order requests
            logPipe << this->describe() << " creating tulip request" << END_LINE;
            std::vector<Flower> tulipsRequest(this->tulipsStock.end() - it->tulips, this->tulipsStock.end());

            logPipe << this->describe() << " creating roses request" << END_LINE;
            std::vector<Flower> rosesRequest(this->rosesStock.end() - it->roses, this->rosesStock.end());

            // Make invoice
            std::string invoice = this->makeInvoice(it->buyer, rosesRequest, tulipsRequest);
            logPipe << this->describe() << " make a new invoice" << END_LINE << END_LINE << invoice << END_LINE;

            // Update stocks
            this->rosesStock.resize(this->rosesStock.size() - it->roses);
            this->tulipsStock.resize(this->tulipsStock.size() - it->tulips);

            // Erase the deliver internet order
            it = this->orders.erase(it);
        } else {
            // Not enough stock
            logPipe << this->describe() << " not enough stock for " << it->buyer << " order" << END_LINE;
            ++it;
        }
    }


    logPipe << this->describe() << " finish trying to deliver remaining internet orders" << END_LINE;
}

void PointOfSale::deliverLocalOrder(const Order & order) {

    unsigned int tulips = order.getTulips();
    unsigned int roses = order.getRoses();

    if (tulips <= this->tulipsStock.size() && roses <= this->rosesStock.size()) {
        // Creates order requests
        logPipe << this->describe() << " creating tulip request" << END_LINE;
        std::vector<Flower> tulipsRequest(this->tulipsStock.end() - tulips, this->tulipsStock.end());

        logPipe << this->describe() << " creating roses request" << END_LINE;
        std::vector<Flower> rosesRequest(this->rosesStock.end() - roses, this->rosesStock.end());
        for (Flower & flower: tulipsRequest) {
			// @checkpoint sp_prepare_bouquet this->id flower.getFlowerId() order.getOrderId() flower.getFlowerName()
		}
        for (Flower & flower: rosesRequest) {
			// @checkpoint sp_prepare_bouquet this->id flower.getFlowerId() order.getOrderId() flower.getFlowerName()
		}

        // Make invoice
        std::string invoice = this->makeInvoice("LocalClient", rosesRequest, tulipsRequest);
        logPipe << this->describe() << " make a new invoice" << END_LINE << END_LINE << invoice << END_LINE;

        // Update stocks
        this->rosesStock.resize(this->rosesStock.size() - roses);
        this->tulipsStock.resize(this->tulipsStock.size() - tulips);
        // @checkpoint sp_serve_order this->id order.getOrderId()
    } else {
        // Not enough stock
        logPipe << this->describe() << " not enough stock for LocalClient order" << END_LINE;
    }
}

std::string PointOfSale::makeInvoice(std::string buyer, const std::vector<Flower> & roses, const std::vector<Flower> & tulips) {
    std::stringstream ss;

    ss << "INVOICE FOR: " << buyer << std::endl;
    ss << std::endl << std::endl;

    ss << "ITEMS:" << std::endl;

    for (const Flower & r: roses) {
        ss << "\t\t" << r.describe() << std::endl;
        protocol.sendFlowerAnalytics(r);
    }

    for (const Flower & t: tulips) {
        ss << "\t\t" << t.describe() << std::endl;
        protocol.sendFlowerAnalytics(t);
    }

    return ss.str();
}
